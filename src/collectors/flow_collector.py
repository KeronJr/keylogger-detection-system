# src/collectors/flow_collector.py
"""Network flow collector using Scapy"""
from scapy.all import sniff, IP, TCP, UDP, conf
import time
from collections import defaultdict
import statistics

class FlowCollector:
    def __init__(self, timeout=5.0):
        self.flows = {}
        self.timeout = timeout
        self.last_check = time.time()
        self.completed = []
        
    def get_key(self, pkt):
        if not pkt.haslayer(IP):
            return None
        ip = pkt[IP]
        if pkt.haslayer(TCP):
            return (ip.src, pkt[TCP].sport, ip.dst, pkt[TCP].dport, 'TCP')
        elif pkt.haslayer(UDP):
            return (ip.src, pkt[UDP].sport, ip.dst, pkt[UDP].dport, 'UDP')
        return None
    
    def process(self, pkt):
        key = self.get_key(pkt)
        if not key:
            return
        
        ts = float(pkt.time)
        plen = len(pkt)
        
        if key not in self.flows:
            self.flows[key] = {
                'first_ts': ts, 'last_ts': ts,
                'fwd_count': 0, 'bwd_count': 0,
                'fwd_bytes': 0, 'bwd_bytes': 0,
                'fwd_lens': [], 'bwd_lens': [],
                'timestamps': [ts],
                'syn': 0, 'ack': 0, 'rst': 0, 'psh': 0, 'urg': 0, 'fin': 0,
                'src': key[0], 'dst': key[2], 'sport': key[1], 'dport': key[3], 'proto': key[4]
            }
        
        f = self.flows[key]
        f['last_ts'] = ts
        f['timestamps'].append(ts)
        
        is_fwd = pkt[IP].src == key[0]
        if is_fwd:
            f['fwd_count'] += 1
            f['fwd_bytes'] += plen
            f['fwd_lens'].append(plen)
        else:
            f['bwd_count'] += 1
            f['bwd_bytes'] += plen
            f['bwd_lens'].append(plen)
        
        if pkt.haslayer(TCP):
            flags = pkt[TCP].flags
            if flags & 0x02: f['syn'] += 1
            if flags & 0x10: f['ack'] += 1
            if flags & 0x04: f['rst'] += 1
            if flags & 0x08: f['psh'] += 1
            if flags & 0x20: f['urg'] += 1
            if flags & 0x01: f['fin'] += 1
        
        now = time.time()
        if now - self.last_check > 1.0:
            self.last_check = now
            self.expire()
    
    def expire(self):
        now = time.time()
        for key in list(self.flows.keys()):
            if now - self.flows[key]['last_ts'] > self.timeout:
                self.completed.append(self.finalize(self.flows.pop(key)))
    
    def finalize(self, f):
        dur = f['last_ts'] - f['first_ts']
        mean = lambda l: statistics.mean(l) if l else 0.0
        std = lambda l: statistics.pstdev(l) if len(l)>1 else 0.0
        iats = [f['timestamps'][i+1]-f['timestamps'][i] for i in range(len(f['timestamps'])-1)]
        
        return {
            'flow_duration': dur,
            'total_fwd_packets': f['fwd_count'],
            'total_bwd_packets': f['bwd_count'],
            'total_fwd_bytes': f['fwd_bytes'],
            'total_bwd_bytes': f['bwd_bytes'],
            'fwd_pkt_len_max': max(f['fwd_lens']) if f['fwd_lens'] else 0,
            'fwd_pkt_len_min': min(f['fwd_lens']) if f['fwd_lens'] else 0,
            'fwd_pkt_len_mean': mean(f['fwd_lens']),
            'fwd_pkt_len_std': std(f['fwd_lens']),
            'bwd_pkt_len_max': max(f['bwd_lens']) if f['bwd_lens'] else 0,
            'bwd_pkt_len_min': min(f['bwd_lens']) if f['bwd_lens'] else 0,
            'bwd_pkt_len_mean': mean(f['bwd_lens']),
            'bwd_pkt_len_std': std(f['bwd_lens']),
            'flow_bytes_per_s': (f['fwd_bytes']+f['bwd_bytes'])/dur if dur>0 else 0,
            'flow_packets_per_s': (f['fwd_count']+f['bwd_count'])/dur if dur>0 else 0,
            'flow_iat_mean': mean(iats),
            'flow_iat_std': std(iats),
            'flow_iat_max': max(iats) if iats else 0,
            'flow_iat_min': min(iats) if iats else 0,
            'fwd_iat_mean': 0, 'fwd_iat_std': 0,
            'bwd_iat_mean': 0, 'bwd_iat_std': 0,
            'syn_count': f['syn'], 'ack_count': f['ack'],
            'rst_count': f['rst'], 'psh_count': f['psh'],
            'urg_count': f['urg'], 'fin_count': f['fin'],
            'subflow_fwd_packets': f['fwd_count'],
            'subflow_bwd_packets': f['bwd_count'],
            'src': f['src'], 'dst': f['dst'],
            'sport': f['sport'], 'dport': f['dport'],
            'proto': f['proto']
        }
    
    def get_completed(self):
        c = self.completed.copy()
        self.completed.clear()
        return c
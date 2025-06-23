// SPDX-License-Identifier: GPL-2.0
#include <uapi/linux/bpf.h>
#include <uapi/linux/if_ether.h>
#include <uapi/linux/ip.h>
#include <uapi/linux/tcp.h>
#include <uapi/linux/udp.h>
#include <linux/in.h>
#include <bcc/proto.h>

#define INTERVAL_NS 1000000000ULL

struct flow_stats_t {
	__u64 timestamp;
	__u32 pkt_count;
	__u32 pkt_len_sum;
	__u32 tcp_count;
	__u32 udp_count;
	__u32 syn_count;
};

BPF_TABLE("percpu_array", u32, struct flow_stats_t, stats, 1);
BPF_TABLE("array", u32, u64, last_ts, 1);

int xdp_prog_main(struct xdp_md *ctx)
{
	//timestamp
	u64 now = bpf_ktime_get_ns();
	u32 key = 0;

	struct flow_stats_t *st = stats.lookup(&key);
	if (!st) return XDP_PASS;
	
	st->pkt_count += 1;
	st->pkt_len_sum += (__u32)(ctx->data_end - ctx->data);
	
	//L2/L3/L4
	void *data = (void *)(unsigned long) ctx->data;
	void *data_end = (void *)(unsigned long)ctx->data_end;

	struct ethhdr *eth = data;
	if ((void *)(eth + 1) > data_end)
		return XDP_PASS;
	
	if (bpf_ntohs(eth->h_proto) != ETH_P_IP)
		goto maybe_flush;
	
	struct iphdr *ip = (struct iphdr *)(eth + 1);
	if ((void *)(ip + 1) > data_end)
		goto maybe_flush;
	
	if (ip->protocol == IPPROTO_TCP) {
		st->tcp_count += 1;
		struct tcphdr *tcp = (void *)(ip + 1);
		if((void *)(tcp + 1) > data_end)
			goto maybe_flush;
		if(tcp->syn)
			st->syn_count += 1;
	} else if (ip->protocol == IPPROTO_UDP) {
		st->udp_count += 1;
	}

maybe_flush:

	__u64 *last = last_ts.lookup(&key);

	if (!last) return XDP_PASS;
	
	if (now - *last > INTERVAL_NS) {
		st->timestamp = now / 1000000000ULL;
		*last = now;
		
		//reset
		 __builtin_memset(st, 0, sizeof(*st));  
        st->timestamp = now / 1000000000ULL;    
	}
	return XDP_PASS;
}


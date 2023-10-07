#!/usr/bin/env python3

from bcc import BPF
from time import sleep


program = """
#include <linux/sched.h>
#include <net/inet_sock.h>

struct data_t {
    u32 pid;
    u64 count;
    char comm[TASK_COMM_LEN];
};

BPF_HASH(syn_count, u32, u64);
BPF_PERF_OUTPUT(events);

int count_syn(struct pt_regs *ctx) {
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);

    if (sk == NULL)
        return 0;

    struct inet_sock *inet = inet_sk(sk);
    u8 protocol = 0;
    bpf_probe_read(&protocol, sizeof(protocol), &inet->sk.__sk_common.skc_protocol);

    if (protocol == IPPROTO_TCP && inet->inet_num > 0) {
        u32 pid = bpf_get_current_pid_tgid();
        u64 *count, zero = 0;
        count = syn_count.lookup_or_init(&pid, &zero);
        if (count) {
            (*count)++;
            if (*count == 1) {
                struct data_t data = {};
                data.pid = pid;
                data.count = *count;
                bpf_get_current_comm(&data.comm, sizeof(data.comm));
                events.perf_submit(ctx, &data, sizeof(data));
            }
        }
    }
    return 0;
}
"""

b = BPF(text=program)
b.attach_kprobe(event="tcp_v4_connect", fn_name="count_syn")

print("Tracing TCP SYN... Ctrl+C to end.")


def print_event(cpu, data, size):
    event = b["events"].event(data)
    print(f"Process: {event.comm.decode('utf-8', 'replace')}, PID: {event.pid}, SYN Count: {event.count}")

b["events"].open_perf_buffer(print_event)


try:
    while True:
        b.perf_buffer_poll()
except KeyboardInterrupt:
    pass

from bcc import BPF
import time

# eBPF 프로그램 정의
program = """

#include <net/sock.h>

typedef struct backlog_key {
    u32 pid;
    char task[TASK_COMM_LEN];
} backlog_key_t;

BPF_HASH(dist, backlog_key_t);

int do_entry(struct pt_regs *ctx) {
    struct sock *sk = (struct sock *)PT_REGS_PARM1(ctx);

    backlog_key_t key = {};
    u64 pid_tgid = bpf_get_current_pid_tgid();
    u32 pid = pid_tgid >> 32;
    key.pid = pid;

    bpf_get_current_comm(&key.task, sizeof(key.task));


    dist.increment(key);

    return 0;
};
"""

b = BPF(text=program)

# `tcp_v4_connect` 함수에 eBPF 프로그램을 연결
b.attach_kprobe(event="inet_csk_accept", fn_name="trace_connect")

print("Tracing tcp_v4_connect... Ctrl-C to end.")
try:
    while True:
        time.sleep(1)  # 10초마다 카운터 값을 출력
        for key, value in b["dist"].items():
            print(f"tcp_v4_connect calls: {value.value}")
except KeyboardInterrupt:
    pass

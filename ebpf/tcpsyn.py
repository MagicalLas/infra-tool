from bcc import BPF
import time

# eBPF 프로그램 정의
program = """
#include <uapi/linux/ptrace.h>

BPF_HASH(connect_count, u64);
u64 zero = 0;

int trace_connect(struct pt_regs *ctx) {
    bpf_trace_printk("tcp_v4_connect called\\n");
    return 0;
}
"""

b = BPF(text=program)

# `tcp_v4_connect` 함수에 eBPF 프로그램을 연결
b.attach_kprobe(event="tcp_v4_syn_recv_sock", fn_name="trace_connect")

print("Tracing tcp_v4_connect... Ctrl-C to end.")
try:
    while True:
        time.sleep(10)  # 10초마다 카운터 값을 출력
        for key, value in b["connect_count"].items():
            print(f"tcp_v4_connect calls: {value.value}")
except KeyboardInterrupt:
    pass

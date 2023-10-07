#!/usr/bin/env python
# @lint-avoid-python-3-compatibility-imports
#
# tcpsynbl      Show TCP SYN backlog.
#               For Linux, uses BCC, eBPF. Embedded C.
#
# USAGE: tcpsynbl [-4 | -6] [-h]
#
# Copyright (c) 2019 Brendan Gregg.
# Licensed under the Apache License, Version 2.0 (the "License").
# This was originally created for the BPF Performance Tools book
# published by Addison Wesley. ISBN-13: 9780136554820
# When copying or porting, include this comment.
#
# 03-Jul-2019   Brendan Gregg   Ported from bpftrace to BCC.

from __future__ import print_function
import argparse
from bcc import BPF
from time import sleep
from struct import pack
from socket import inet_ntop, AF_INET, AF_INET6

# load BPF program
bpf_text = """
#include <net/sock.h>

typedef struct backlog_key {
    char task[TASK_COMM_LEN];
    u32 pid;
    u32 saddr;
    u32 daddr;
    u16 lport;
    u16 dport;
} backlog_key_t;

BPF_HISTOGRAM(dist, backlog_key_t);

int do_entry(struct pt_regs *ctx) {
    // get pid
    u32 pid = bpf_get_current_pid_tgid() >> 32;

    struct sock *sk = (struct sock *)PT_REGS_PARM2(ctx);

    // get details
    u16 family = 0, lport = 0, dport;

    // build datas
    backlog_key_t key = {};
    key.saddr = sk->__sk_common.skc_rcv_saddr;
    key.daddr = sk->__sk_common.skc_daddr;
    key.lport = sk->__sk_common.skc_num;
    key.dport = sk->__sk_common.skc_dport;
    key.pid = pid;

    bpf_get_current_comm(&key.task, sizeof(key.task));

    // add data
    dist.increment(key, 1);

    return 0;
};

"""

b = BPF(text=bpf_text)

b.attach_kprobe(event="reqsk_alloc", fn_name="do_entry")

print("Tracing SYN backlog size. Ctrl-C to end.")

try:
    sleep(99999999)
except KeyboardInterrupt:
    print()

dist = b.get_table("dist")
for k, v in dist.items():
    saddr = inet_ntop(AF_INET, pack("I",k.saddr))
    daddr = inet_ntop(AF_INET, pack("I",k.daddr))
    print([f"{k.pid}+{k.task}({saddr}:{k.lport}->{daddr}:{k.dport})", v.value])

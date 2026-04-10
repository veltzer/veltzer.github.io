---
tags:
  - linux
  - windows
  - performance
date: 2026-03-29
---

# Linux io_uring vs Windows I/O: A Technical Comparison

## The State of Async I/O

High-performance servers, databases, and storage engines all face the same
bottleneck: how to perform massive amounts of I/O without drowning in system
call overhead. Linux and Windows have taken fundamentally different approaches
to this problem, and the gap has widened significantly since Linux 5.1 introduced
io_uring in 2019.

## What is io_uring?

io_uring is a Linux kernel interface for asynchronous I/O built around two
lock-free ring buffers shared between user space and the kernel: a submission
queue (SQ) and a completion queue (CQ). The application pushes I/O requests
into the SQ, and the kernel delivers results into the CQ — all without system
calls in the hot path.

Key properties:

* **Zero-copy submission** — requests are written directly into shared memory.
  No `syscall` envelope is needed per operation once the rings are set up.
* **Batching** — a single `io_uring_enter()` call can submit hundreds of
  operations and reap completions at the same time.
* **Polled mode** — for ultra-low-latency NVMe workloads, the kernel can
  busy-poll for completions, eliminating interrupt overhead entirely.
* **Registered buffers and file descriptors** — pre-registering resources
  removes repeated kernel lookups, shaving microseconds per operation.
* **Linked operations** — chains of dependent I/O operations can be submitted
  as a single unit, executed in sequence by the kernel.
* **Fixed-size, pre-allocated rings** — no allocations on the hot path.

## Windows Async I/O Mechanisms

Windows offers several overlapping async I/O mechanisms, each from a different era:

### I/O Completion Ports (IOCP)

IOCP, introduced in Windows NT 3.5 (1994), is the primary high-performance
async I/O mechanism on Windows. An application creates a completion port, associates
file handles with it, issues overlapped I/O operations, and dequeues completions
from the port.

* Thread-pool aware — the kernel limits concurrency to avoid context-switch storms.
* Well integrated with Winsock for network I/O.
* Every I/O operation is a system call. There is no batching or shared-memory shortcut.

### Overlapped I/O

The foundation under IOCP. Each I/O call takes an `OVERLAPPED` structure and
completes asynchronously. Completion notification comes via IOCP, event objects,
or alertable wait (APC). The per-operation system call overhead remains.

### Registered I/O (RIO)

Introduced in Windows 8 / Server 2012, RIO is Microsoft's attempt at a
higher-performance network I/O path. It pre-registers buffers and uses
submission/completion queues — conceptually similar to io_uring but limited
to network sockets only. RIO never gained wide adoption and is rarely used
outside of specialized financial trading applications.

## Head-to-Head Comparison

### System Call Overhead

This is where io_uring wins decisively. IOCP requires one system call per I/O
operation issued and one per completion dequeued. io_uring can submit and reap
thousands of operations with zero system calls using shared-memory polling mode,
or at most one `io_uring_enter()` call for a full batch. On workloads with
millions of small I/O operations per second, this difference alone can mean
30-50% higher throughput.

### Generality

io_uring supports virtually every I/O operation the kernel offers: read, write,
fsync, poll, accept, connect, send, recv, openat, close, statx, rename, unlink,
mkdir, and many more. It has effectively become a general-purpose async syscall
interface.

IOCP is primarily designed for file and socket I/O. RIO is sockets only.
Windows has no equivalent of io_uring's ability to perform arbitrary filesystem
operations asynchronously through a unified interface.

### Buffer Management

io_uring allows pre-registering fixed buffers that the kernel maps once. Provided
buffer groups allow the kernel to pick buffers on behalf of the application,
eliminating a round-trip for receive operations.

IOCP requires pinning pages for each overlapped operation. RIO pre-registers
buffers but only for network I/O. There is no equivalent of io_uring's provided
buffer groups for file I/O on Windows.

### Kernel Bypass and Polling

io_uring's SQPOLL mode spawns a kernel thread that continuously polls the
submission queue, meaning the application never enters the kernel at all in
steady state. Combined with NVMe polled mode, this achieves latencies close
to SPDK-style kernel bypass without giving up the safety of kernel-mediated I/O.

Windows has no equivalent. The closest is a user-mode driver framework (UMDF)
or a custom kernel driver, both of which are far more complex to develop and
deploy.

### Linked and Dependent Operations

io_uring supports operation chaining: read a file, then write to a socket,
then fsync — all submitted as a single linked chain. The kernel executes them
in order without returning to user space between steps.

IOCP has no equivalent. Each dependent operation must be submitted from user
space after the previous one completes, adding a round-trip per link in the chain.

### Maturity and Ecosystem

IOCP has 30 years of production use. It is well-understood, well-documented,
and deeply integrated into the Windows ecosystem (.NET, Win32, Winsock). Virtually
every Windows server application uses it. The debugging and profiling tooling
(ETW, xperf, WPA) is mature.

io_uring is younger (2019) and has gone through several security hardening
iterations. Early kernel versions had io_uring-related CVEs, and some
distributions (notably Google's production kernels and earlier versions of
Docker's seccomp profiles) disabled it entirely for a period. The API has
stabilized considerably since Linux 5.15+, and major projects (PostgreSQL,
RocksDB, NGINX, Tokio, liburing) now use it in production.

## Advantages of io_uring Over Windows I/O

* **Dramatically lower per-operation overhead** due to shared-memory ring buffers
  and batched submission.
* **Unified interface** for all I/O types — file, network, filesystem metadata — rather
  than separate mechanisms for each.
* **Kernel-side polling** eliminates syscall overhead entirely for latency-sensitive workloads.
* **Operation chaining** reduces round-trips for multi-step I/O sequences.
* **Provided buffer groups** let the kernel manage receive buffers, simplifying
  application code and reducing memory waste.
* **Rapid evolution** — new operations and optimizations are added in every kernel release.
* **Open source** — anyone can read, audit, and contribute to the implementation.

## Advantages of Windows I/O Over io_uring

* **Decades of stability** — IOCP's API has been frozen for 30 years. No surprise
  breaking changes.
* **Thread-pool integration** — IOCP's built-in concurrency throttling makes it
  harder to write a server that melts under load.
* **Superior documentation and tooling** — Microsoft's IOCP documentation, ETW
  tracing, and WPA analysis are polished.
* **No security teething pains** — IOCP's attack surface has been hardened over
  three decades, while io_uring is still accumulating CVE fixes.
* **RIO for niche use** — for pure network workloads, RIO offers some of io_uring's
  benefits without the complexity.
* **Broader language support** — C#/.NET async I/O is built directly on IOCP,
  making high-performance I/O accessible without manual ring buffer management.

## Disadvantages of io_uring

* **Complexity** — the API is powerful but large. Correct use requires understanding
  ring buffer semantics, memory ordering, and submission queue entry (SQE) flags.
  Libraries like liburing help, but the abstraction is inherently more complex
  than "call ReadFile with OVERLAPPED."
* **Security track record** — io_uring has been a recurring source of privilege
  escalation vulnerabilities. The large kernel attack surface is an ongoing concern.
* **Kernel version sensitivity** — features and fixes vary significantly across
  kernel versions. An application targeting io_uring must either require a
  recent kernel or implement fallback paths.
* **Debugging difficulty** — tracing I/O through shared-memory ring buffers is
  harder than tracing system calls. Standard strace does not capture io_uring
  operations by default.

## Disadvantages of Windows I/O

* **Syscall-per-operation overhead** — the fundamental architectural limitation.
  No amount of optimization can match a zero-syscall path.
* **Fragmented API surface** — IOCP, RIO, overlapped I/O, and APCs are separate
  mechanisms with different semantics, leading to confusion and bugs.
* **No true async filesystem metadata operations** — operations like rename, delete,
  and stat are synchronous on Windows. Applications needing async metadata operations
  must use thread pools, which defeats the purpose.
* **RIO stagnation** — Microsoft's most io_uring-like API has seen minimal
  development since its introduction and remains network-only.
* **Closed source** — impossible to audit, debug at the kernel level, or contribute
  fixes without Microsoft's involvement.

## The Bottom Line

io_uring represents a generational leap in I/O interface design. It addresses
the fundamental inefficiency that plagued all previous async I/O models — the
per-operation system call — and replaces it with shared-memory communication
that can achieve millions of IOPS with minimal CPU overhead.

Windows IOCP remains competent and battle-tested, but its architecture is
showing its age. Microsoft has not shipped a comparable modern I/O interface,
and RIO was a half-step that never reached its potential.

For new high-performance systems — databases, storage engines, proxies,
messaging systems — io_uring on Linux is the clear technical winner. The
performance difference is not marginal; it is architectural. Applications
that previously needed kernel bypass frameworks like DPDK or SPDK can now
achieve comparable performance through io_uring while remaining within the
standard kernel I/O path.

The Linux kernel's willingness to rethink fundamental interfaces, even at the
cost of short-term complexity and security growing pains, has produced a
measurably superior I/O subsystem. Windows, constrained by decades of backward
compatibility commitments and a more conservative kernel development culture,
has fallen behind on this front.

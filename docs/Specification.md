## Credit-Based FIFO Specification

### Interface
Inputs:
- clk
- rst_n
- wr_valid
- rd_ready
- wr_data

Outputs:
- wr_ready
- rd_valid
- rd_data
- credit_count

### Behavior
- FIFO depth = DEPTH
- credit_count initialized to DEPTH
- wr_ready asserted when credit_count > 0
- rd_valid asserted when FIFO not empty
- wr occurs when wr_valid & wr_ready
- rd occurs when rd_valid & rd_ready

### Corner Cases
- Simultaneous wr & rd must not corrupt pointers
- credit_count must not overflow or underflow
- Pointer wraparound must be correct
- rd_data must be stable when rd_valid=1 and rd_ready=0
- No extra credits allowed

### Reset
- All state cleared
- credit_count = DEPTH


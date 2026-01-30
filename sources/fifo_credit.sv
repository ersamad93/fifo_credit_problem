module fifo_credit #(
    parameter int DATA_WIDTH = 32,
    parameter int DEPTH = 8,
    localparam int ADDR_W = $clog2(DEPTH)
)(
    input  logic                 clk,
    input  logic                 rst_n,

    input  logic                 wr_valid,
    output logic                 wr_ready,
    input  logic [DATA_WIDTH-1:0] wr_data,

    output logic                 rd_valid,
    input  logic                 rd_ready,
    output logic [DATA_WIDTH-1:0] rd_data,

    output logic [ADDR_W:0]       credit_count
);

    logic [DATA_WIDTH-1:0] mem [DEPTH];
    logic [ADDR_W-1:0] wr_ptr, rd_ptr;
    logic [ADDR_W:0]   fifo_count;

    wire do_wr = wr_valid && wr_ready;
    wire do_rd = rd_valid && rd_ready;

    assign wr_ready = (credit_count > 0);
    assign rd_valid = (fifo_count > 0);

    always_ff @(posedge clk) begin
        if (!rst_n) begin
            wr_ptr       <= '0;
            rd_ptr       <= '0;
            fifo_count  <= '0;
            credit_count<= DEPTH;
        end else begin
            case ({do_wr, do_rd})
                2'b10: begin
                    mem[wr_ptr] <= wr_data;
                    wr_ptr <= wr_ptr + 1'b1;
                    fifo_count <= fifo_count + 1'b1;
                    credit_count <= credit_count - 1'b1;
                end
                2'b01: begin
                    rd_ptr <= rd_ptr + 1'b1;
                    fifo_count <= fifo_count - 1'b1;
                    credit_count <= credit_count + 1'b1;
                end
                2'b11: begin
                    mem[wr_ptr] <= wr_data;
                    wr_ptr <= wr_ptr + 1'b1;
                    rd_ptr <= rd_ptr + 1'b1;
                    // counts unchanged
                end
            endcase
        end
    end

    assign rd_data = mem[rd_ptr];

endmodule

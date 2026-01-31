module fifo_credit #(
    parameter int DATA_WIDTH = 32,
    parameter int DEPTH = 8,
    parameter int ADDR_W = 3)
    (
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

//Insert RTL Code here


endmodule



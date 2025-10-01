
(* blackbox *)
module gf180mcu_fd_ip_sram__sram512x8m8wm1 (
	CLK,
	CEN,
	GWEN,
	WEN,
	A,
	D,
	Q
);

input           CLK;
input           CEN;    //Chip Enable
input           GWEN;   //Global Write Enable
input   [7:0]  	WEN;    //Write Enable
input   [8:0]   A;
input   [7:0]  	D;
output	[7:0]	Q;

  assign Q = 0;

endmodule

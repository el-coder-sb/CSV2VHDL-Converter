	--
	-- Measurement data of my_decoded_file.vhd starts here
	--
	wait for   0.0 ns;		spi_clk_stimu01_sl_s		<=	'1';
	wait for   0.0 ns;		spi_mosi_stimu01_sl_s		<=	'1';
	wait for   0.0 ns;		spi_clk_stimu02_sl_s		<=	'1';
	wait for   0.0 ns;		spi_mosi_stimu02_sl_s		<=	'1';
	wait for 9000.0 ns;		spi_clk_stimu01_sl_s		<=	'0';
	wait for   0.0 ns;		spi_mosi_stimu01_sl_s		<=	'0';
	wait for   0.0 ns;		spi_clk_stimu02_sl_s		<=	'0';
	wait for   0.0 ns;		spi_mosi_stimu02_sl_s		<=	'0';
	wait for 1000.0 ns;		spi_clk_stimu01_sl_s		<=	'1';
	wait for   0.0 ns;		spi_clk_stimu02_sl_s		<=	'1';
	wait for   1.0 ns;		spi_mosi_stimu01_sl_s		<=	'1';
	wait for   9.0 ns;		spi_mosi_stimu02_sl_s		<=	'1';
	wait for 3990.0 ns;		spi_clk_stimu02_sl_s		<=	'0';
	wait for   0.0 ns;		spi_clk_stimu01_sl_s		<=	'0';
	wait for   0.0 ns;		spi_mosi_stimu01_sl_s		<=	'0';
	wait for   0.0 ns;		spi_mosi_stimu02_sl_s		<=	'0';
	wait for 8000.0 ns;		spi_clk_stimu02_sl_s		<=	'1';
	wait for   0.0 ns;		spi_clk_stimu01_sl_s		<=	'1';
	wait for   0.0 ns;		spi_mosi_stimu02_sl_s		<=	'1';
	wait for  10.0 ns;		spi_mosi_stimu01_sl_s		<=	'1';

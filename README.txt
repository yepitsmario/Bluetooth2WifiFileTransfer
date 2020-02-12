Source Code is "BTtcp_filetrans.py"

Requirements/Assumptions:
	*PyblueZ library is installed. (Check the source website linked below)
	*Linux Computer
	*Python version 2.X
	*Uses Bluetooth not Bluetooth LE
	*Works with small sized files and any filetypes, maybe big files
	
Operating Instructions
	*On both devices, do this concurrently
	*CD to the python file location
	*Run terminal
		* Be sure bluetooth is on and visible!
		* type in: "sudo python BTtcp_filetrans.py"
	* Follow the prompts to connect and send file or directory
	* click enter to refresh when receiving things, this is due to locking up from the raw_input() calls
	* When receiving a file, wait for the "received file" message
		
Known Bugs:
	*Connection through bluetooth does not timeout when both are trying to connect as clients. Restart the programs
	
	*When connecting through bluetooth, it will throw an exception. Ignore this, the code should continue to run and
	 connect via Wifi

References:
	https://github.com/karulis/pybluez
	http://blog.kevindoran.co/bluetooth-programming-with-python-3/
	https://wiki.python.org/moin/TcpCommunication
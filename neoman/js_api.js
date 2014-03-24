Neo = {};

(function(){
	//Internal
	function bytes_to_hex(bytes) {
		var hex = "";
		for(var i=0; i<bytes.length; i++) {
			var b = bytes[i].toString(16);
			if(b.length == 1) b = "0" + b;
			hex += b;
		}
		return hex;
	}

	//Public API
	Neo.aid = _JS_API.aid;
	Neo.log = _JS_API.log;

	Neo.send_apdu = function(data) {
		var resp = _JS_API.send_apdu(data);
		var bytes = [];
		for(var i=0; i<resp.length; i+=2) {
			bytes.push(parseInt(resp.substr(i, 2), 16));
		}
		return bytes;
	};

	Neo.select = function() {
		var len_hex = bytes_to_hex([Neo.aid.length / 2]);
		return Neo.send_apdu("00a40400" + len_hex + Neo.aid);
	};

	Neo.send_ok = function(data) {
		var bytes = Neo.send_apdu(data);
		var len = bytes.length;
		if(bytes[len-2] == 0x90 && bytes[len-1] == 0x00) {
			return bytes.slice(0, len-2);
		} else {
			Neo.log("ERROR req: "+data+", resp: "+bytes_to_hex(bytes));
		}
	};
})();

function domReady(fn) {
	if (
		document.readyState === "complete" ||
		document.readyState === "interactive"
	) {
		setTimeout(fn, 1000);
	} else {
		document.addEventListener("DOMContentLoaded", fn);
	}
}

domReady(function () {
	// If found you qr code
	function onScanSuccess(decodeText, decodeResult) {
		// Update the input field with the QR code result
		document.getElementById("ticketInput").value = decodeText;
		// Trigger the search button
		document.getElementById("searchTicket").click();
	}

	let htmlscanner = new Html5QrcodeScanner("my-qr-reader", {
		fps: 10,
		qrbos: 250,
	});
	htmlscanner.render(onScanSuccess);
});

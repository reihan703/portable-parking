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
		// Send the scanned text to the server
		fetch("/manage_tickets", {
			method: "POST",
			headers: {
				"Content-Type": "application/json",
			},
			body: JSON.stringify({ ticket: decodeText }),
		})
			.then((response) => {
				if (response.redirected) {
					// Redirect to the new URL
					window.location.href = response.url;
				} else {
					return response.json();
				}
			})
			.then((data) => {
				console.log("Success:", data);
				// Handle success response if needed
			})
			.catch((error) => {
				console.error("Error:", error);
			});
	}

	let htmlscanner = new Html5QrcodeScanner("my-qr-reader", {
		fps: 10,
		qrbos: 250,
	});
	htmlscanner.render(onScanSuccess);
	// Stop the QR code scanner
	htmlscanner
		.stop()
		.then((ignore) => {
			// QR Code scanning stopped successfully
			console.log("QR Code scanning stopped.");

			// Send the result to the server using a POST request
		})
		.catch((err) => {
			// Handle errors when stopping the QR code scanner
			console.error("Failed to stop QR Code scanning.", err);
		});
});

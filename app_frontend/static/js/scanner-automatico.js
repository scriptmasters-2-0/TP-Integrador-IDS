
let html5QrCode;
let procesando = false;

const btnIniciar = document.getElementById('btn-iniciar');
const btnDetener = document.getElementById('btn-detener');
const txtResultado = document.getElementById('resultado');

function obtenerIdReservaEscaneada(decodedText) {
    try {
        const datosQr = JSON.parse(decodedText);
        const idReserva = Number(datosQr.id_reserva);
        if (!Number.isInteger(idReserva) || idReserva <= 0) {
            return null;
        }
        return idReserva;
    } catch (error) {
        return null;
    }
}

btnIniciar.addEventListener('click', () => {
    procesando = false;
    html5QrCode = new Html5Qrcode("preview");
    Html5Qrcode.getCameras().then(devices => {
        if (devices && devices.length > 0) {
            const cameraId = devices[0].id;
            return html5QrCode.start(
                cameraId, 
                {
                    fps: 15, qrbox: { width: 400, height: 400 },
                },
                async (decodedText, decodedResult) => {
                    if (procesando) {
                        return;
                    }
                    procesando = true;
                    try {
                        console.log("QR leido:", decodedText);
                        const idReserva = obtenerIdReservaEscaneada(decodedText);
                        if (idReserva === null) {
                            txtResultado.innerText = "QR inválido. Escanee un comprobante de reserva.";
                            return;
                        }

                        console.log("id:", idReserva);
                        txtResultado.innerText = "Procesando #" + idReserva;
                        await apagarCamara();
                        const response = await fetch(`/biblioteca/reservas/${idReserva}/scan`, { method: "PATCH" });
                        const resultado = await response.json();
                        console.log(resultado);
                        txtResultado.innerText = "Estado nuevo:" + resultado.estado_reserva;
                    
                        apagarCamara(); 
                    } catch (error) {
                        console.error(error);
                        txtResultado.innerText = "No se pudo procesar el QR. Intente nuevamente.";
                    } finally {
                        procesando = false;
                    }
                },
                (errorMessage) => {
                    
                }
            );
        } else {
            throw new Error("No se detectó ninguna cámara física en el sistema.");
        }
    }).then(() => {
        btnIniciar.disabled = true;
        btnDetener.disabled = false;
        txtResultado.innerText = "Cámara encendida. Acerque un código QR.";
    }).catch((err) => {
        // Captura de errores (por si se deniega el permiso o falla el hardware)
        txtResultado.innerText = "Error al acceder a la cámara: " + err;
    });
});

btnDetener.addEventListener('click', apagarCamara);

function apagarCamara() {
    if (html5QrCode && html5QrCode.isScanning) {
        return html5QrCode.stop().then(() => {
            btnIniciar.disabled = false;
            btnDetener.disabled = true;
            txtResultado.innerText = "Cámara apagada.";
        });
    }
    return Promise.resolve();
}
/* REQUIRE: jQuery */

/***********************************************/
/********** VARIABLE DECLARATION ***************/
/***********************************************/
var canvas, color, penWidth, ctx2d, pLast;
var wSock, wsId;
var isDrawing, isBrushDrawing, isCanvasSaved;

var brushImg = null;

var SIZE_UNDO_STACK = 20;
var undoStack = new Array();

var brushBank = {};

var recCanvas, recCanvasCtx;
var recCanvasW, recCanvasH;

var audioCtx, srcNode, analyzNode;
var mediaRecorder, mediaStream;
var audioData;

/***********************************************/
/********** VARIABLE DECLARATION ***************/
/***********************************************/



/***************************************/
/********** DOM SETTINGS ***************/
/***************************************/
$("document").ready(function () {
	canvas = $("#canvas");
	color = $("#input-color-picker");
	penWidth = $("#pen-size");
	// brushImg = $("img#img-pen-style")[0];
	ctx2d = canvas[0].getContext("2d");
	pLast = { 'x': 0, 'y': 0 };

	isDrawing = false;
	isBrushDrawing = false;
	isCanvasSaved = false;

	wSock = new WebSocket(`ws://${window.location.host}/soundOekaki/room1234`);
	wsId = -1;

	recCanvas = $("#canvas-analyzer");
	recCanvasCtx = recCanvas[0].getContext("2d");


	audioCtx = new AudioContext();

	/* Init: HTML Main Canvas */
	htmlCanvasRetinization(canvas, ctx2d);

	// Set: lineWidth
	ctx2d.lineWidth = 10;
	ctx2d.lineCap = "round";
	ctx2d.lineJoin = "bevel";

	/* Init: HTML Analyzer Canvas */
	htmlCanvasRetinization(recCanvas, recCanvasCtx);
	recCanvasW = parseInt(recCanvas.prop("width"));
	recCanvasH = parseInt(recCanvas.prop("height"));
	recCanvasCtx.fillStyle = "#eee";
	recCanvasCtx.fillRect(0, 0, recCanvasW, recCanvasH);



	/* Init: Event Listener */
	canvas.on({
		"mousedown": function (ev) {
			isCanvasSaved = false;
			isDrawing = true;

			// Send Brush data when isBrushDrawing
			if (isBrushDrawing) {
				wSock.send(JSON.stringify({
					"action": "SEND_BRUSH",
					"payload": {
						"id": wsId,
						"imgData": imgToBase64(brushImg)
					}
				}));
			}
		},

		"mouseout": function (ev) {
			isDrawing = false;
			wSock.send(JSON.stringify({
				"action": 'EOD' // End of Drawing
			}));
		},

		"mouseup": function (ev) {
			isDrawing = false;
			wSock.send(JSON.stringify({
				"action": 'EOD' // End of Drawing
			}));
		},

		"mousemove": function (ev) {
			if (isDrawing) {
				// Save Canvas;
				if (!isCanvasSaved) {
					canvasPush()
					isCanvasSaved = true;
				}
				// Drawing
				mousePos = { 'x': ev.offsetX, 'y': ev.offsetY };
				drawing(mousePos);
			}
			pLast = { 'x': ev.offsetX, 'y': ev.offsetY };
		},
		"mouseout": function (ev) {
			isDrawing = false;
		},
        "touchstart": function (ev) {
            isCanvasSaved = false;
            // isDrawing = true;
            // Send Brush data when isBrushDrawing
            if (isBrushDrawing) {
                wSock.send(JSON.stringify({
                    "action": "SEND_BRUSH",
                    "payload": {
                        "id": wsId,
                        "imgData": imgToBase64(brushImg)
                    }
                }));
            }
            pLast = getTouchPos(ev);;
        },
        "touchend": function (ev) {
            // isDrawing = false;
            wSock.send(JSON.stringify({
                "action": 'EOD' // End of Drawing
            }));
        },
        "touchmove": function (ev) {
            touchPos = getTouchPos(ev);
            // if (isDrawing) {
                // Save Canvas;
                if (!isCanvasSaved) {
                    canvasPush()
                    isCanvasSaved = true;
                }
                // Drawing
                drawing(touchPos);

            // }
            pLast = touchPos;
        }

	});

	$("#btn-clear-canvas").on("click", function (ev) {
		ctx2d.clearRect(0, 0, canvas[0].width, canvas[0].height);
	});

	$("#btn-undo").on("click", function (ev) {
		canvasPop();
	});

	$("#btn-color-picker").on("click", function () {
		$("#input-color-picker").trigger("click");
	});

	$("#btn-draw-select").on("click", function () {
		if (brushImg == null) {
			$("#placeholder-message-dialog").html(`
				<div id='message-dialog' class='alert alert-danger alert-dismissible fade show' role='alert'>
					<span id='message-text'>
						<strong>Error! </strong>: ブラシが設定されていません。
					</span>
					<button type='button' class='close' data-dismiss='alert' aria-label='Close'>
						<span aria-hidden='true'>&times;</span>
					</button>
				</div>
			`);
			return;
		}

		if (isBrushDrawing) {
			$("#btn-draw-select").text("Pen");
		} else {
			$("#btn-draw-select").text("Brush");
		}
		isBrushDrawing = !isBrushDrawing;
	});

	// モバイルだと下までスクロールするとresizeが発火してcanvasが消えてしまう
    // Todo : モバイルとpcで分ける？
	// $(window).on("resize", function (ev) {
	// 	htmlCanvasRetinization(canvas, ctx2d);
	// });

	$(".number-spinner button").on("click", function () {
		var btn = $(this);
		var oldValue = btn.closest(".number-spinner").find("input").val().trim();
		var newVal = 0;

		if (btn.attr("data-dir") == "up") {
			newVal = parseInt(oldValue) + 1;
		} else {
			if (oldValue > 1) {
				newVal = parseInt(oldValue) - 1;
			} else {
				newVal = 1;
			}
		}

		btn.closest(".number-spinner").find("input").val(newVal);
	});

	/*************************************/
	/******* AUDIO RECORD MODAL **********/
	/*************************************/

	// Init: Audio I/O
	navigator.mediaDevices.getUserMedia({ audio: true }).then(stream => {
		mediaStream = stream;
		srcNode = audioCtx.createMediaStreamSource(stream);
		analyzNode = audioCtx.createAnalyser();
		analyzNode.fftSize = 2048;
		srcNode.connect(analyzNode);

		function drawAnalyzer() {
			const fftData = new Uint8Array(analyzNode.fftSize);
			analyzNode.getByteTimeDomainData(fftData);
			const barWidth = recCanvasW / analyzNode.fftSize;

			// Reset Canvas
			recCanvasCtx.fillStyle = "#fff";
			recCanvasCtx.fillRect(0, 0, recCanvasW, recCanvasH);

			for (let i = 0; i < analyzNode.fftSize; ++i) {
				const value = fftData[i];
				const percent = value / 255;
				const height = (recCanvasH / 2) * percent;
				const offset = (recCanvasH / 2) - height;

				if ($("#btn-rec-start").hasClass("btn-danger")) {
					recCanvasCtx.fillStyle = 'lime';
				} else {
					recCanvasCtx.fillStyle = 'red';
				}

				recCanvasCtx.fillRect(i * barWidth, offset, barWidth, 2);
			}

			requestAnimationFrame(drawAnalyzer);
		}

		drawAnalyzer();
	}).catch(error => {
		console.log(error);
	});

	/* EVENT: fired before show */
	$("#recModal").on("show.bs.modal", function () {
		// Init: Modal
		$("#canvas-analyzer").show();
		$("#btn-modal-close").prop("disabled", "");
		$("#btn-rec-start").prop("disabled", "");
		$("#btn-rec-start").removeClass("btn-primary");
		$("#btn-rec-start").addClass("btn-danger");
		$("#modal-brush-img").hide();
		$("#message-modal-rec").html("<big>録音するには<strong>Start</strong>を押してください</big>");

		// Init: Media Recorder (FIX: Remove mime type)
		mediaRecorder = new MediaRecorder(mediaStream);
		audioData = new Array();

		// Set: Event Listener
		mediaRecorder.addEventListener('dataavailable', function (ev) {
			if (ev.data.size > 0) {
				audioData.push(ev.data);
				console.log("Pushed");
			}
		});
		mediaRecorder.addEventListener('stop', function () {
			// UPDATE VIEW
			$("#canvas-analyzer").hide();
			$("#btn-modal-close").prop("disabled", true);
			$("#btn-rec-start").prop("disabled", true);
			$("#message-modal-rec").html('<font color="blue"><i class="fas fa-spinner fa-spin"></i> 生成中 ... </font>');


			/* POST audio data to server using Ajax */
			// REF: http://semooh.jp/jquery/api/ajax/jQuery.ajax/options/
			$.ajax({
				type: "POST",
				url: `https://${window.location.host}/pen`,
				contentType: "application/octet-stream",
				data: (new Blob(audioData, { type: 'audio/webm' })),
				processData: false,
				dataType: "json",
				success: function (data, dataType) {
					// @param      data: Response data
					// @param  dataType: Data type of 'data'

					// Set Brush Image
					brushImg = base64ToImg(data.data);

					// Show Result at Modal
					$("#modal-brush-img").show();
					$("#modal-brush-img").append(brushImg);
					$("#modal-brush-img>img").css("width", "128px");
					$("#message-modal-rec").html('<div style="text-align: center;"><strong>ブラシが生成されました！</strong></div>');

					// Show Result at Header
					$("#header-current-brush>img").remove();
					$("#header-current-brush").append(brushImg.cloneNode());
					$("#header-current-brush>img").css("width", "32px");
					$("#header-current-brush>img").css("border", "1px solid #bbb;");

				},
				error: function (XMLHttpRequest, textStatus, errorThrown) {
					// @param  XMLHttpRequest: XMLHttpRequest object
					// @param      textStatus: String of error message
					// @param     errorThrown: unknonwn ...

					console.log("Ajax: POST Failed !");
					console.log(` textStatus: ${textStatus}`);
					console.log(`errorThrown: ${errorThrown}`);
				}

			});

		});

	});

	/* EVENT: fired after closed */
	$("#recModal").on("hidden.bs.modal", function () {
		// Stop MediaRecorder
		if (mediaRecorder.state === "recording") {
			mediaRecorder.stop();
		}
	});


	$("#btn-rec-start").on("click", function () {
		if ($("#btn-rec-start").hasClass("btn-danger")) {
			// Change View
			$("#btn-rec-start").removeClass("btn-danger");
			$("#btn-rec-start").addClass("btn-primary");
			$("#btn-rec-start").text("Stop Rec");
			$("#message-modal-rec").html("<big><strong><font color='red'>録音中...</font></strong></big>");

			// Delete Previous Brush
			$("#modal-brush-img>img").remove();

			// Canvas Reset
			recCanvasCtx.fillStyle = "#fff";
			recCanvasCtx.fillRect(0, 0, recCanvasW, recCanvasH);

			// Start Record
			mediaRecorder.start();

		} else {
			// Change View
			$("#btn-rec-start").removeClass("btn-primary");
			$("#btn-rec-start").addClass("btn-danger");
			$("#btn-rec-start").text("Start Rec");
			$("#message-modal-rec").html("<big>録音するには<strong>Start</strong>を押してください</big>");

			// Canvas Reset
			recCanvasCtx.fillStyle = "#eee";
			recCanvasCtx.fillRect(0, 0, recCanvasW, recCanvasH);

			// Stop Record
			mediaRecorder.stop();
		}

	});

	/*************************************/
	/******* AUDIO RECORD MODAL **********/
	/*************************************/


	// WebSocket: Message arrived
	wSock.onmessage = function (ev) {
		var data = JSON.parse(ev.data);
		var action = data.action;
		var payload = data.payload;


		console.log(`WebSocket: Received Message ! (action = ${action})`);
		switch (action) {
			case "ENTER_USER":
				console.log("Welcome, n00b !");
				$("#txt-card-header").text("Users: " + payload.num);
				break;
				
			case "ID":
				wsId = payload.id;
				console.log(`WebSocket: Receive ID ! (id = ${wsId})`)
				break;

			case "DRAW":
				syncCanvas(payload);
				break;

			case "EOD": // EOD := End Of Drawing
				break;

			case "SEND_BRUSH":
				brushBank[payload.id] = base64ToImg(payload.imgData);

			default:
				break;
		}
	}

});

/***************************************/
/********** DOM SETTINGS ***************/
/***************************************/



/************************************************/
/********** FUNCTION DECLARATIONS ***************/
/************************************************/

// Support Retina Display ( scale = 200% )
function htmlCanvasRetinization(jqCanvas, ctx) {
	var canvasCssW = parseInt(jqCanvas.css("width"));
	var canvasCssH = parseInt(jqCanvas.css("height"));


	jqCanvas.prop("width", canvasCssW * 2);
	jqCanvas.prop("height", canvasCssH * 2);

	ctx.scale(2, 2);
}


function calcDistance(p0, p1) {
	return Math.sqrt(Math.pow(p1.x - p0.x, 2) + Math.pow(p1.y - p0.y, 2));
}

function calcAngle(p0, p1) {
	return Math.atan2(p1.y - p0.y, p1.x - p0.x);
}

<<<<<<< HEAD
function drawing(evMouse) {
	var pCurrent = { 'x': evMouse.offsetX, 'y': evMouse.offsetY };
=======
function drawing(pCurrent) {
	var penImg = $("img#img-pen-style")[0];
>>>>>>> 328bc0ef51a39d663e817f6a17eeb59aadc194a8

	var dist = calcDistance(pLast, pCurrent);
	var angl = calcAngle(pLast, pCurrent);

	ctx2d.beginPath();

	// Set: Line Style
	if (!isBrushDrawing) {
		ctx2d.lineCap = ctx2d.lineJoin = "round";
		ctx2d.strokeStyle = color.val();
		ctx2d.lineWidth = parseInt(penWidth.val());
	}

	for (var i = 0; i < dist; i++) {
		x = pLast.x + i * Math.cos(angl);
		y = pLast.y + i * Math.sin(angl);

		if (isBrushDrawing) {
			// Draw Brush
			ctx2d.drawImage(brushImg, x - 0.5 * brushImg.naturalWidth, y - 0.5 * brushImg.naturalHeight);
		} else {
			// Draw Line
			ctx2d.lineTo(x, y);
		}
		// Send Drawing via WebSocket
		sendCanvasWS(x, y);
	}
	ctx2d.stroke();
}

// Store canvas from canvas stack
function canvasPush() {
	var w = ctx2d.canvas.width;
	var h = ctx2d.canvas.height;

	var imgData = ctx2d.getImageData(0, 0, w, h);

	if (undoStack.length == SIZE_UNDO_STACK) {
		undoStack.shift();
	}
	undoStack.push(imgData);

	$("#btn-undo").removeAttr("disabled");
	$("#btn-undo").text("Undo (" + undoStack.length + ")");
}

// Restore canvas from canvas stack
function canvasPop() {
	var imgData = undoStack.pop();

	if (undoStack.length == 0) {
		$("#btn-undo").attr("disabled", "disabled");
	}

	if (typeof imgData !== "undefined") {
		ctx2d.putImageData(imgData, 0, 0);
	} else {
		console.log("Stack is Empty !");
	}

	$("#btn-undo").text("Undo (" + undoStack.length + ")");
}

// Send canvas using WebSocket
function sendCanvasWS(x, y) {
	var payload = {
		'action': "DRAW",
		'payload': {
			'id': wsId,
			'type': (isBrushDrawing) ? 'brush' : 'pen',
			'ctx': {
				'lineCap': ctx2d.lineCap,
				'lineJoin': ctx2d.lineJoin,
				'strokeStyle': ctx2d.strokeStyle,
				'lineWidth': ctx2d.lineWidth
			},
			'pos': {
				'x': x,
				'y': y
			}
		}
	};

	wSock.send(JSON.stringify(payload));
}

// Sync canvas using WebSocket
function syncCanvas(payload) {

	ctx2d.beginPath();

	if (payload.type === "brush") {
		var brushBankImg = brushBank[payload.id];

		if (typeof brushBankImg === "undefined") {
			console.log("Error!: Brush not found");
		} else {
			// Draw Brush
			ctx2d.drawImage(brushBankImg, payload.pos.x - 0.5 * brushBankImg.naturalWidth, payload.pos.y - 0.5 * brushBankImg.naturalHeight);
		}

	} else {
		// Set: Line Style
		ctx2d.lineCap = payload.ctx.lineCap;
		ctx2d.lineJoin = payload.ctx.lineJoin;
		ctx2d.strokeStyle = payload.ctx.strokeStyle;
		ctx2d.lineWidth = payload.ctx.lineWidth;

		// Draw Line
		ctx2d.lineTo(payload.pos.x, payload.pos.y);
		ctx2d.stroke();
	}
}

// HTMLImageElement --> Base64 String
function imgToBase64(htmlImageElement) {
	// REF: https://qiita.com/yasumodev/items/e1708f01ff87692185cd
	var htmlCanvas = document.createElement('canvas');


	htmlCanvas.width = htmlImageElement.width;
	htmlCanvas.height = htmlImageElement.height;
	htmlCanvas.getContext('2d').drawImage(htmlImageElement, 0, 0);

	return htmlCanvas.toDataURL('image/png');
}

// Base64 String --> HTMLImageElement
function base64ToImg(strBase64) {
	// REF: https://qiita.com/yasumodev/items/e1708f01ff87692185cd
	var img = new Image();
	img.src = strBase64;
	return img;
}

function getTouchPos(ev) {
	canvasPos = ev.target.getBoundingClientRect();
	return { 'x': ev.touches[0].clientX - canvasPos.left, 'y': ev.touches[0].clientY - canvasPos.top };
}

/************************************************/
/********** FUNCTION DECLARATIONS ***************/
/************************************************/

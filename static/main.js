/* REQUIRE: jQuery */

/***********************************************/
/********** VARIABLE DECLARATION ***************/
/***********************************************/
var canvas, color, penWidth, brushImg, ctx2d, pLast;
var wSock, wsId;
var isDrawing, isBrushDrawing, isCanvasSaved;

var SIZE_UNDO_STACK = 20;
var undoStack = new Array();

var brushBank = {};



$("document").ready(function () {
	canvas = $("#canvas");
	color = $("#input-color-picker");
	penWidth = $("#pen-size");
	brushImg = $("img#img-pen-style")[0];
	ctx2d = canvas[0].getContext("2d");
	pLast = { 'x': 0, 'y': 0 };

	isDrawing = false;
	isBrushDrawing = false;
	isCanvasSaved = false;

	
	wSock = new WebSocket(`ws://${window.location.host}/soundOekaki/room1234`);
	wsId = -1;


	/* init: HTML Canvas */
	htmlCanvasRetinization();
	// set lineWidth
	ctx2d.lineWidth = 10;
	ctx2d.lineCap = "round";
	ctx2d.lineJoin = "bevel";

	/* init: Event Listener */
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
				drawing(ev);
			}
			pLast = { 'x': ev.offsetX, 'y': ev.offsetY };
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
		if (isBrushDrawing) {
			$("#btn-draw-select").text("Pen");
		} else {
			$("#btn-draw-select").text("Brush");
		}
		isBrushDrawing = !isBrushDrawing;
	});

	$(window).on("resize", function (ev) {
		htmlCanvasRetinization();
	});

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

	// WebSocket: Message arrived
	wSock.onmessage = function (ev) {
		var data = JSON.parse(ev.data); 
		// var data = ev.data;
		var action = data.action;
		var payload = data.payload;

		
		console.log(`WebSocket: Received Message ! (action = ${action})`);
		switch (action) {
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

/* Function Declarations */
function htmlCanvasRetinization() {
	var canvasCssW = parseInt(canvas.css("width"));
	var canvasCssH = parseInt(canvas.css("height"));


	canvas.prop("width", canvasCssW * 2);
	canvas.prop("height", canvasCssH * 2);

	ctx2d.scale(2, 2);
}


function calcDistance(p0, p1) {
	return Math.sqrt(Math.pow(p1.x - p0.x, 2) + Math.pow(p1.y - p0.y, 2));
}

function calcAngle(p0, p1) {
	return Math.atan2(p1.y - p0.y, p1.x - p0.x);
}

function drawing(evMouse) {
	var pCurrent = { 'x': evMouse.offsetX, 'y': evMouse.offsetY };
	var penImg = $("img#img-pen-style")[0];

	var dist = calcDistance(pLast, pCurrent);
	var angl = calcAngle(pLast, pCurrent);

	// console.log(`Dist: ${dist}, Angle: ${angl}`);

	ctx2d.beginPath();

	// Set line style
	if (!isBrushDrawing) {
		ctx2d.lineCap = ctx2d.lineJoin = "round";
		ctx2d.strokeStyle = color.val();
		ctx2d.lineWidth = parseInt(penWidth.val());
	}

	for (var i = 0; i < dist; i++) {
		x = pLast.x + i * Math.cos(angl);
		y = pLast.y + i * Math.sin(angl);

		if (isBrushDrawing) {
			// Draw brush
			ctx2d.drawImage(penImg, x - 0.5 * penImg.naturalWidth, y - 0.5 * penImg.naturalHeight);
		} else {
			// Draw line
			ctx2d.lineTo(x, y);
			// Send Drawing via WebSocket
		}
		sendCanvasWS(x, y);
	}
	ctx2d.stroke();
}

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

// Sync Canvas using WebSocket
function syncCanvas(payload){

	ctx2d.beginPath();
	
	if (payload.type === "brush") {
		var penImg = brushBank[payload.id];

		if (typeof penImg === "undefined") {
			console.log("Error!: Brush not found");
		} else {
			// Draw brush
			ctx2d.drawImage(penImg, payload.pos.x - 0.5 * penImg.naturalWidth, payload.pos.y - 0.5 * penImg.naturalHeight);
		}

	} else {
		// Set line style
		ctx2d.lineCap = payload.ctx.lineCap;
		ctx2d.lineJoin = payload.ctx.lineJoin;
		ctx2d.strokeStyle = payload.ctx.strokeStyle;
		ctx2d.lineWidth = payload.ctx.lineWidth;

		// Draw line
		ctx2d.lineTo(payload.pos.x, payload.pos.y);
		ctx2d.stroke();
	}
}


function imgToBase64 (htmlImageElement) {
	// REF: https://qiita.com/yasumodev/items/e1708f01ff87692185cd
	var htmlCanvas = document.createElement('canvas');


	htmlCanvas.width = htmlImageElement.width;
	htmlCanvas.height = htmlImageElement.height;
	htmlCanvas.getContext('2d').drawImage(htmlImageElement, 0, 0);

	return htmlCanvas.toDataURL('image/png');
}

function base64ToImg (strBase64) {
	// REF: https://qiita.com/yasumodev/items/e1708f01ff87692185cd
	var img = new Image();
	img.src = strBase64;
	// Debug
	$("#label-brush-img").text("RECEIVED!!");
	$("#brush-img")[0].src = strBase64;
	return img;
}

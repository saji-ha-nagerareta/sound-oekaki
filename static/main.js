/* REQUIRE: jQuery */

$("document").ready(function () {
	var canvas = $("#canvas");
	var color = $("#input-color-picker");
	var width = $("#pen-size");
	var ctx2d = canvas[0].getContext("2d");
	var pLast = { 'x': 0, 'y': 0 };

	var isDrawing = false;
	var isBrushDrawing = false;
	var isCanvasSaved = false;
	var SIZE_UNDO_STACK = 20;
	var undoStack = new Array();

	var ws = new WebSocket("ws://localhost:8888/soundOekaki/room1234");


	/* init: HTML Canvas */
	htmlCanvasRetinization(canvas, ctx2d);
	// set lineWidth
	ctx2d.lineWidth = 10;
	// set endpoints
	ctx2d.lineCap = "round";
	ctx2d.lineJoin = "bevel";

	/* init: Event Listener */
	canvas.on({
		"mousedown": function (ev) {
			isCanvasSaved = false;
			isDrawing = true;
		},
		"mouseout": function (ev) {
			var payload = {
				"action": 'EOD' // End of Drawing
			};
			isDrawing = false;
			ctx2d.beginPath();
			ws.send(JSON.stringify(payload));
		},
		"mouseup": function (ev) {
			var payload = {
				"action": 'EOD' // End of Drawing
			};
			isDrawing = false;
			ctx2d.beginPath();
			ws.send(JSON.stringify(payload));
		},
		"mousemove": function (ev) {
			if (isDrawing) {
				// Save Canvas;
				if (!isCanvasSaved) {
					canvasPush(undoStack, ctx2d, SIZE_UNDO_STACK)
					isCanvasSaved = true;
				}
				// Drawing
				drawing(isBrushDrawing, ctx2d, ev, pLast, color, width, ws);
			}
			pLast = { 'x': ev.offsetX, 'y': ev.offsetY };
		},
		"mouseout": function (ev) {
			isDrawing = false;
		}
	});

	$("#btn-clear-canvas").on("click", function (ev) {
		ctx2d.clearRect(0, 0, canvas[0].width, canvas[0].height);
		ctx2d.beginPath();
	});

	$("#btn-undo").on("click", function (ev) {
		canvasPop(undoStack, ctx2d);
	});

	$("#btn-color-picker").on("click", function () {
		$("#input-color-picker").trigger("click");
	});

	$("#btn-draw-select").on("click", function () {
		console.log("isBrushDrawing: " + isBrushDrawing.toString());
		if (isBrushDrawing) {
			$("#btn-draw-select").text("Pen");
		} else {
			$("#btn-draw-select").text("Brush");
		}
		isBrushDrawing = !isBrushDrawing;
	});

	$(window).on("resize", function (ev) {
		htmlCanvasRetinization(canvas, ctx2d);
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

	if (!isBrushDrawing){
		// WebSocket: Message arrived
		ws.onmessage = function (ev) {
			syncCanvas(ctx2d, ev);
		}
	}

});

/* Function Declarations */
function htmlCanvasRetinization(jqCanvas, canvas2dCtx) {
	var canvasCssW = parseInt(jqCanvas.css("width"));
	var canvasCssH = parseInt(jqCanvas.css("height"));


	jqCanvas.prop("width", canvasCssW * 2);
	jqCanvas.prop("height", canvasCssH * 2);

	canvas2dCtx.scale(2, 2);
}


function calcDistance(p0, p1) {
	return Math.sqrt(Math.pow(p1.x - p0.x, 2) + Math.pow(p1.y - p0.y, 2));
}

function calcAngle(p0, p1) {
	return Math.atan2(p1.y - p0.y, p1.x - p0.x);
}

function drawing(flag, canvas2dCtx, evMouse, pLast, jqColor, jqWidth, wSock) {
	var ctx = canvas2dCtx;
	var pCurrent = { 'x': evMouse.offsetX, 'y': evMouse.offsetY };
	var penImg = $("img#img-pen-style")[0];

	var dist = calcDistance(pLast, pCurrent);
	var angl = calcAngle(pLast, pCurrent);

	// console.log(`Dist: ${dist}, Angle: ${angl}`);

	// Set line style
	if (!flag) {
		ctx.lineCap = ctx.lineJoin = "round";
		ctx.strokeStyle = jqColor.val();
		ctx.lineWidth = parseInt(jqWidth.val());
	}


	for (var i = 0; i < dist; i++) {
		x = pLast.x + i * Math.cos(angl);
		y = pLast.y + i * Math.sin(angl);

		if (flag) {
			// Draw brush
			ctx.drawImage(penImg, x - 0.5 * penImg.naturalWidth, y - 0.5 * penImg.naturalHeight);
		} else {
			// Draw line

			ctx.lineTo(x, y);
			sendCanvasWS(wSock, ctx, x, y);
			ctx.stroke();
		}
	}
}

function canvasPush(stack, ctx, LIMIT) {
	var w = ctx.canvas.width;
	var h = ctx.canvas.height;

	var imgData = ctx.getImageData(0, 0, w, h);

	if (stack.length == LIMIT) {
		stack.shift();
	}
	stack.push(imgData);

	$("#btn-undo").removeAttr("disabled");
	$("#btn-undo").text("Undo (" + stack.length + ")");

	return;
}

function canvasPop(stack, ctx) {
	var imgData = stack.pop();

	if (stack.length == 0) {
		$("#btn-undo").attr("disabled", "disabled");
	}

	if (typeof imgData !== "undefined") {
		ctx.putImageData(imgData, 0, 0);
		console.log("Canvas Restored !");
	} else {
		console.log("Stack is Empty !");
	}
	$("#btn-undo").text("Undo (" + stack.length + ")");
}

// Send canvas using WebSocket
function sendCanvasWS(wSock, canvas2dctx, x, y) {
	var ws  = wSock, 
			ctx = canvas2dctx;
	var payload = {
		'action': "DRAW",
		'payload': {
			'ctx': {
				'lineCap': ctx.lineCap,
				'lineJoin': ctx.lineJoin,
				'strokeStyle': ctx.strokeStyle,
				'lineWidth': ctx.lineWidth
			},
			'pos': {
				'x': x,
				'y': y
			}
		}
	};

	ws.send(JSON.stringify(payload));
}

// Sync Canvas using WebSocket
function syncCanvas(canvas2dCtx, ev){
	var data = JSON.parse(ev.data);
	var ctx = canvas2dCtx;

	console.log(data);

	var action = data.action;
	var payload = data.payload;

	switch (action) {
		case "DRAW":
			ctx.lineCap = payload.ctx.lineCap;
			ctx.lineJoin = payload.ctx.lineJoin;
			ctx.strokeStyle = payload.ctx.strokeStyle;
			ctx.lineWidth = payload.ctx.lineWidth;

			ctx.lineTo(payload.pos.x, payload.pos.y);
			ctx.stroke();
			break;
	
		case "EOD":
			ctx.beginPath();
			break;
		
		default:
			break;
	}

}

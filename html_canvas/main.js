/* REQUIRE: jQuery */

$("document").ready(function () {
	var canvas = $("#canvas");
	var color = $("#input-color-picker");
	var width = $("#pen-size");
	var ctx2d = canvas[0].getContext("2d");

	var isDrawing = false;
	var isBrushDrawing = false;
	var isCanvasSaved = false;
	var SIZE_UNDO_STACK = 20;
	var undoStack = new Array();


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
			isDrawing = false;
			ctx2d.beginPath();
		},
		"mouseup": function (ev) {
			isDrawing = false;
			ctx2d.beginPath();
		},
		"mousemove": function (ev) {
			if (isDrawing) {
				// Save Canvas;
				if (!isCanvasSaved) {
					canvasPush(undoStack, ctx2d, SIZE_UNDO_STACK)
					isCanvasSaved = true;
				}
				// Drawing
				drawing(isBrushDrawing, ctx2d, ev, color, width);
			}
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

});

/* Function Declarations */
function htmlCanvasRetinization(jqCanvas, canvas2dCtx) {
	var canvasCssW = parseInt(jqCanvas.css("width"));
	var canvasCssH = parseInt(jqCanvas.css("height"));


	jqCanvas.prop("width", canvasCssW * 2);
	jqCanvas.prop("height", canvasCssH * 2);

	canvas2dCtx.scale(2, 2);
}

function drawing(flag, canvas2dCtx, mouseEvent, jqColor, jqWidth) {
	var ctx = canvas2dCtx;
	var ev = mouseEvent;
	var penImg = $("img#img-pen-style")[0];


	if (flag) {
		ctx.drawImage(penImg, ev.offsetX - 0.5 * penImg.naturalWidth, ev.offsetY - 0.5 * penImg.naturalHeight);
	} else {
		// Draw line
		ctx.lineCap = ctx.lineJoin = "round";
		ctx.strokeStyle = jqColor.val();
		ctx.lineWidth = parseInt(jqWidth.val());
		ctx.lineTo(ev.offsetX, ev.offsetY);
		ctx.stroke();
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

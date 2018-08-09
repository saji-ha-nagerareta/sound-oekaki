// ref from: https://kigiroku.com/frontend/canvas_draw.html
var drawing = false;
// 前回の座標を記録する（初期値：０）
var before_x = 0;
var before_y = 0;
var canvas = document.getElementById('canvas');
var ctx = canvas.getContext('2d');

// 描画の処理
function draw_canvas(e) {
	// console.log(`Position: (${e.offsetX}, ${e.offsetY})`);
	// drawingがtrueじゃなかったら返す
	if (!drawing) {
		return
	};

	var rect = e.target.getBoundingClientRect();
	// var x = e.clientX - rect.left;
	var x = e.offsetX;
	// var y = e.clientY - rect.top;
	var y = e.offsetY;
	var w = document.getElementById('width').value;
	var color = document.getElementById('input-color-picker').value;
	var r = parseInt(color.substring(1, 3), 16);
	var g = parseInt(color.substring(3, 5), 16);
	var b = parseInt(color.substring(5, 7), 16);


	// 描画
	ctx.lineCap = 'round';
	ctx.strokeStyle = 'rgb(' + r + ',' + g + ',' + b + ')';
	ctx.lineWidth = w;
	ctx.beginPath();
	ctx.moveTo(before_x, before_y);
	ctx.lineTo(x, y);
	ctx.stroke();
	ctx.closePath();
	// 描画最後の座標を前回の座標に代入する
	before_x = x;
	before_y = y;
}

function draw_brush(e) {
	console.log(`Position: (${e.offsetX}, ${e.offsetY})`);
	if (!drawing) {
		return;
	}

	// var img = document.getElementById("img-pen-style")
	var penImg = $('#img-pen-style')[0];

	var rect = e.target.getBoundingClientRect();
	var x = e.clientX - rect.left;
	var y = e.clientY - rect.top;
	var w = penImg.naturalWidth;
	var h = penImg.naturalHeight;

	ctx.drawImage(penImg, x - 0.5 * w, y - 0.5 * h);
}

// クリアボタンクリック時
// クリアボタンクリックした時にアラートを表示
function delete_canvas() {
	// ret = confirm('canvasの内容を削除します。');
	// // アラートで「OK」を選んだ時
	// if (ret == true) {
	// 	ctx.clearRect(0, 0, canvas.width, canvas.height);
	// }
	ctx.clearRect(0, 0, canvas.width, canvas.height);
}
var pen = document.getElementById('pencil');
var era = document.getElementById('eraser');

// 鉛筆と消しゴムの切り替え
function tool(btnNum) {
	// クリックされボタンが鉛筆だったら
	if (btnNum == 1) {
		ctx.globalCompositeOperation = 'source-over';
		pen.className = 'active';
		era.className = '';
	}
	// クリックされボタンが消しゴムだったら
	else if (btnNum == 2) {
		ctx.globalCompositeOperation = 'destination-out';
		pen.className = '';
		era.className = 'active';
	}
}

// Canvas サイズをレスポンシブに変更
// REF: https://stackoverflow.com/questions/34772957/how-to-make-canvas-responsive
// function resize() {
// 	$("#canvas").outerHeight($(window).height() - $("#canvas").offset().top - Math.abs($("#canvas").outerHeight(true) - $("#canvas").outerHeight()));
// }

// Ready DOM

function canvasRetinization() {
	// Retina Support
	var canvasX = parseInt(window.getComputedStyle(canvas).getPropertyValue('width'));
	var canvasY = parseInt(window.getComputedStyle(canvas).getPropertyValue('height'));

	canvas.width = canvasX * 2;
	canvas.height = canvasY * 2;
	ctx.scale(2, 2);
}

$(document).ready(function () {
	// -----EVENT LISTENER-----
	// canvas.addEventListener('mousemove', draw_brush);
	canvas.addEventListener('mousemove', draw_canvas);

	canvas.addEventListener('mousedown', function (e) {
		drawing = true;
		var rect = e.target.getBoundingClientRect();
		before_x = e.clientX - rect.left;
		before_y = e.clientY - rect.top;
	});

	canvas.addEventListener('mouseup', function () {
		drawing = false;
	});

	// マウスが描画領域から出た場合の処理
	canvas.addEventListener('mouseover', function () {
		drawing = false;
	});

	$('#btn-color-picker').click(function () {
		$('#input-color-picker').trigger('click');
	});

	// for Debug
	// $('#input-color-picker').click(function () {
	// console.log("Clicked!");
	// });
	// $('#btn-color-picker').click(function () {
	// 	console.log("Clicked!");
	// });
	// $(document).on('click', '#btn-color-picker', function () {
	// console.log("Clicked!");
	// })

	canvasRetinization();
	$(window).on("resize", canvasRetinization);
});

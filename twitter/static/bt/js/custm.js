function changeDp(ee) {
    console.log(ee.files[0]);
    var reader = new FileReader();
    reader.onload = function (e) {
        // console.log(e)
        $('.dp').attr('src',e.target.result)

    };

    reader.readAsDataURL(ee.files[0]);
   }
$('.dp_selector').change(function () {
    changeDp(this);
});


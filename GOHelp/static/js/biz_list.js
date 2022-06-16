$(function() {
  	$.ajaxSetup({
    	headers: { "X-CSRFToken": token }
  	});
  	$("#biz_info").on("click", "#bmk", function() {
  			id = $(this).parent().find("p").html();
			username = username;
			data = {
				"id" : id,
				"username" : username
			};
		if($(this).is(":checked")) {
			$.ajax({
				type : 'POST',
				url : bookmark_in,
				data : JSON.stringify(data),
			});
			$(this).parent().attr("style", "content: url(" + bookmark_fill + ");");
		}else {
			$.ajax({
				type : 'POST',
				url : bookmark_out,
				data : JSON.stringify(data),
			});
			$(this).parent().attr("style", "content: url(" + bookmark + ");");
		}
	});

	$('html, body').animate({
		scrollTop: $('#biz_info').offset().top
	}, 0);
  });
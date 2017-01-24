
$(document).ready(function(){
  console.log('hello world');
  // Add smooth scrolling to all links in navbar + footer link

	// Show/Hide logo based on scroll position
	
	var $document = $(document);
	
  $document.scroll(function() {
	  if ($document.scrollTop() >= 200) {
	    // user scrolled 50 pixels or more;
	    // do stuff
			console.log('MORE');
			$('.navbarHeaderLogo').fadeIn('fast');
	  } else {
	    console.log('LESS');
			$('.navbarHeaderLogo').fadeOut('fast');
	  }
	});
	

	//
  $(".navbar a, footer a[href='#myPage']").on('click', function(event) {

   // Make sure this.hash has a value before overriding default behavior
  if (this.hash !== "") {

    // Prevent default anchor click behavior
    event.preventDefault();

    // Store hash
    var hash = this.hash;

    // Using jQuery's animate() method to add smooth page scroll
    // The optional number (900) specifies the number of milliseconds it takes to scroll to the specified area
    $('html, body').animate({
      scrollTop: $(hash).offset().top
    }, 900, function(){

      // Add hash (#) to URL when done scrolling (default click behavior)
      window.location.hash = hash;
      });
    } // End if
  });
})
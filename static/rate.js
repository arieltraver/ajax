// JavaScript File to add event-handlers to "rate" a movie

// a simple response handler you can use in raw debugging or demos

function showResponse(resp) {
    console.log('response is: ', resp);
}

// The response handler that the app uses in practice. It gets a response from the back end that looks like:

// {error: false, tt: 456, avg: 3.5}

function processAverage(resp) {
    console.log('response is ',resp);
    // I didn't ask you to do this error reporting
    if(resp.error) {
        // inserting into an error section would 
        // probably be better than an alert
        alert('Error: '+resp.error);
    }
    var tt = resp.tt;
    var avg = resp.avg;
    console.log("New average for movie "+tt+" is "+avg);
    $("[data-tt="+tt+"]").find(".avgrating").text(avg);
}

/* global url_to_rate progressive_on uid */
/* The preceding globals are defined in the movie-list.html template */

// This code adds a delegated event handler to the #movies-list table that takes care of
// (1) making the chosen rating bold and
// (2) posting the Ajax request.

// Have to wrap this in a document.ready because this file is loaded in the head.
$(function () { 
$("#movies-list").on('click',
                     '.movie-rating',
    function (event) {
        if(!progressive_on) return;

        if( event.target != this) return;
        $(this).closest("td").find("label").css("font-weight","normal");
        $(this).css("font-weight","bold");
        var tt = $(this).closest("[data-tt]").attr("data-tt");
        var stars = $(this).find("[name=stars]").val();
        // references the uid variable set by the template
        console.log("user "+uid+" rates movie "+tt+" as "+stars);
        $.post(url_to_rate,
               {'tt': tt, 'stars': stars},
               processAverage, // response callback
               'json');
    });
});

// ================================================================
// Above is all the real work. Below are functions you can use for
// testing in the JavaScript console:


// core function to rate a movie via POST to base url and update the page

function rateMovie(tt, stars) {
    $.post(url_for_post_rating, {'tt': tt, 'stars': stars}, processAverage, 'json');
}

// All these functions use the base_url + tt URL

// gets the current rating and updates the page

function getRating(tt) {
    $.ajax(url_for_rating+tt, {method: 'GET',
                               success: processAverage});
}

// uses the PUT method to replace the current rating and updates the page

function putRating(tt, stars) {
    $.ajax(url_for_rating+tt, {method: 'PUT',
                               data: {stars: stars},
                               success: processAverage});
}

// deletes the current user's rating and updates the page

function deleteRating(tt) {
    $.ajax(url_for_rating+tt, {method: 'DELETE',
                               success: processAverage});
}

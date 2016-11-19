var SUCCESS = 200; //Value returned by services when everything is ok
var NUM_ICONS = 7;
var initialized = false; //Flag to ensure initialization occrus only once

var currentpage = '#home';

$(document).bind('pagecreate', 'home', function( e ){

	if (initialized) return;

	initialized = true;
	updateLoginInfo();

	/******************************************/
	/* Bind events
	/******************************************/

	$("#profile_icon").on( "click", function(event) {
		var src = $("#profile_icon")[0].src;
		var pieces = src.split("/");
		var current = pieces.slice(-1)[0];
		var numicon = parseInt(current.substring(4,current.length-4));
		numicon = (numicon >= NUM_ICONS ? 1 : numicon + 1);
		$("#profile_icon")[0].src = pieces.slice(0,-1).join("/") + "/user" + numicon + ".png";
	});

	$( "#menu_select" ).change(function() {
		var sel = $( "#menu_select option:selected" ).val(); 
		$(currentpage).toggle();
		if (sel == 1) { //Home
			currentpage =  '#home';
		}
		if (sel == 2) { //Bet
			currentpage =  '#option2';
		}
		if (sel == 3) { //Friends
			currentpage =  '#option3';
		}
		if (sel == 4) { //Statistics
			currentpage =  '#option4';
		}
		$(currentpage).show();
	});	
	
	$("#test1").on( "click", function(event) {
		showDialog("Good luck!", "Bet completed", "OK", "-3", "images/reusmeyang.png");	
	});


	$(document).delegate('#dialog-window a', 'click', function (event) {
		var backref = $("#backref")[0].value;
		if (backref.substring(0,1) == "-") {
			event.preventDefault();
//			$("#dialog-window").dialog('close');
			window.history.go(parseInt(backref));
		} else {
			event.preventDefault();
			$.mobile.changePage($(backref));
		}
	});

	$( "#login_select" ).change(function() {
		var sel = $( "#login_select option:selected" ).val(); 
		if (sel == 2) { //Profile
			$('#profile_user')[0].value = username;
			$('#profile_alias')[0].value = user_alias;
			$('#profile_mail')[0].value = user_mail;
			$('#profile_icon')[0].src = "images/users/" + user_icon;
			$('#login_select').val(username).selectmenu('refresh');
			$.mobile.changePage($('#profile'));
		}
		if (sel == 3) { //Logout
			username = ANONYMOUS;
			localStorage.username = username;
			updateLoginInfo();
			$(currentpage).toggle();
			currentpage =  '#home';
			$(currentpage).show();
			$('#menu_select').val(1).selectmenu('refresh');
		}
	});

	$("#login_ok").on( "click", function() {
		var success = function(data){
			ret = data[0].result
			if (data[0].status != SUCCESS) {
				$("#login_error")[0].innerText = ret;
			} else {
				username = $("#login_username")[0].value;
				user_alias = ret[0].name;
				user_mail = ret[0].mail;
				user_icon = ret[0].icon;
				if ($('#login_remember')[0].value == 'on') {
					localStorage.username = username;
					localStorage.alias = user_alias;
					localStorage.mail = user_mail;
					localStorage.icon = user_icon;
				}
				updateLoginInfo();
				event.preventDefault();
				window.history.back();
			}
		};
		var account = $("#login_username")[0].value;
		var pwd = $("#login_password")[0].value;
		if( account != '' && pwd != '') {
			var service = "login";
			$.post(SERVER_URL + "/" + service, {account: account, password: pwd}, success, "jsonp");
		}
		return false;
	});

	$("#login_button").on( "click", function() {
		$("#login_error")[0].innerText = "";
	});

	$("#profile_ok").on( "click", function() {
		var success = function(data){
			if (data[0].status != SUCCESS) {
				$("#profile_error")[0].innerText = data[0].result;
			} else {
				username = $('#profile_user')[0].value;
				user_alias = $('#profile_alias')[0].value;
				user_mail = $('#profile_mail')[0].value;
				user_icon = $('#profile_icon')[0].src.split("images/users/")[1];
				localStorage.username = username;
				localStorage.alias = user_alias;
				localStorage.mail = user_mail;
				localStorage.icon = user_icon;
				showUserInfo();
				event.preventDefault();			
				window.history.go(-2);
			}
		};
		event.preventDefault();			
		var account = $('#profile_user')[0].value;
		var	alias = $('#profile_alias')[0].value;
		var mail = $('#profile_mail')[0].value;
		var pwd = $('#profile_password')[0].value;
		var icon = $('#profile_icon')[0].src.split("images/users/")[1];
		var service;
		var data;
		if (username == ANONYMOUS) { 	//Sign up
			service = "apply";
			data = {username: account, alias: alias, mail: mail, password: pwd, icon: icon};
		} else {						//Change profile
			service = "changeprofile";
			data = {username: account, alias: alias, mail: mail, icon: icon};
		}
		$.post(SERVER_URL + "/" + service, data, success, "jsonp");
	});


$( document ).bind( "pageshow", function( e ){
	if ($.mobile.activePage.attr('id') == 'profile') {
		var user = $('#profile_user');
		if (username == ANONYMOUS) { //Sign up
			user.textinput('enable');
			user[0].value = "";
			$('#profile_alias')[0].value = "";
			$('#profile_mail')[0].value = "";
			$('#profile_password')[0].value = "";
			$('#profile_password').show();
			$('#profile_password_lbl').show();
		} else {
			user.textinput('disable');
			user[0].value = username;
			$('#profile_alias')[0].value = username;
			$('#profile_mail')[0].value = username + "@gmail.com";
			$('#profile_password').hide();
			$('#profile_password_lbl').hide();
		}
	}
});

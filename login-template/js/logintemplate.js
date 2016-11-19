var ANONYMOUS = "anonymous";
//var SERVER_URL = "http://localhost:13080";
var SERVER_URL = "http://login-template-server.appspot.com";

var username = localStorage.username;
if (!username) username = ANONYMOUS;
var user_alias = localStorage.alias;
if (!user_alias) user_alias = ANONYMOUS;
var user_mail = localStorage.mail;
if (!user_mail) user_mail = '';
var user_icon = localStorage.icon;
if (!user_icon) user_icon = '';

/* Update the contents of several pages according to current user
   This function is called whenever a login or logout event occurs. */
function updateLoginInfo() {
	showLoginButtons();
	showUserInfo();
	getGroups();
	getPendingInvitations();
};

/* Enable login buttons depending on current username */
function showLoginButtons() {
	if (username == ANONYMOUS) {
		$('#login_button').show();
		$('#login_menu').hide();
	} else {
		$('#login_button').hide();
		$('#login_menu').show();
		$('#login_select').val(user_alias).selectmenu('refresh');
	}
};

/* Show alias and icon */
function showUserInfo() {
	if (username == ANONYMOUS) {
	} else {
		$("#loginimg")[0].src = "images/users/" + user_icon;
		$('#user_alias')[0].innerHTML = user_alias;
		$('#login_select').val(user_alias).selectmenu('refresh');
	}
};

/* Generic confirmation window */
function showDialog(text, title, button, backref, img) {
	$('#dialog-window').remove();
	var dialog = '<div data-role="dialog" id="dialog-window">' + 
				'<div data-role="content" data-theme="e">' +
				'<center> <h3 class="ui-title">' + (title || '') + '</h3> </center>' +
				'<p> <center>' + text + '</p> </center>';
	if (img) dialog += '<center><img class ="img_dialog" src="' + img + '"></center>';
	dialog += '<center><p><a data-role="button" href="#">' + (button || "Ok") + '</a></p> </center> <BR>' +
				'<input type="hidden" id="backref" value="' + (backref || "#footmaster") + '"></input></div></div>';
	$('body').append(dialog);
	$.mobile.changePage($('#dialog-window'), { role : 'dialog' });
}

/* Generic asking question window */
function getAskDialog(button_label, ident, message) {
	var content = '<a href="#ask_';
	content += ident;
	content += '" data-rel="popup" data-position-to="window" data-transition="pop" class="ui-btn ui-corner-all ui-shadow ui-btn-inline ui-icon-delete ui-btn-icon-left ui-btn-b">';
	content += button_label;
	content += '</a><div data-role="popup" id="ask_';
	content += ident;
	content += '" data-overlay-theme="e" data-theme="e" data-dismissible="false" style="max-width:400px;">\
					<div data-role="header" data-theme="e">\
					<h1>Confirmation</h1>\
					</div>\
					<div role="main" class="ui-content">';
	content += '<h3 class="ui-title">' + message + '</h3>';
	content +='<p>This action cannot be undone.</p>';
	content += '<center><a id="' + ident;
	content += '" href="#" class="ui-btn ui-corner-all ui-shadow ui-btn-inline ui-btn-b" data-rel="back">Yes</a>\
					<a href="#" class="ui-btn ui-corner-all ui-shadow ui-btn-inline ui-btn-b" data-rel="back">No</a>\
					</center></div>\
				</div>';
	return content;
}
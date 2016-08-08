
requirejs.config({
	baseUrl: "/static/",
	paths: {
		domReady: "libs/require/domReady.min",
		angular: "libs/angular/angular.min",
		jquery: "libs/jquery/jquery.min",
		foundation: "libs/foundation/foundation.min",
		uiRouter: "libs/angular/angular-ui-router.min",
	},
	shim: {
		angular: {
				exports: "angular",
			},
		foundation: {
				deps: ["jquery"],
				exports: "foundation",
			},
		uiRouter: {
				deps: ["angular"],
			},
	},
	waitSeconds: 15,
});

requirejs.onError = function(error) {
	alert(error);
	location.reload();
}

require(
	["domReady!", "angular", "jquery", "foundation", "uiRouter", "js/module/home"],
	function(domReady, angular, jquery, foundation, uiRouter, home)
	{
		$(document).foundation();

		home.start();
	}
);

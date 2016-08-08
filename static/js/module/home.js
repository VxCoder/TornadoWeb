
define(

	//模块依赖
	["js/module/common"],

	//模块定义
	function(common) {

		var module = {};

		module.start = function()
		{
			common.trace("模块加载完成");
		};

		return module;

	}

);

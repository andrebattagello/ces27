(function($, document, window) {

	var tooltips = (function() {
		function activateAll () {
			var tooltips = $("*[rel=tooltip]");

			tooltips.tooltip();
		}

		return {
			activate: activateAll
		};
	}());


	var popovers = (function() {
		function insertPopover(id, title, contents) {
			$(id).attr('rel', 'popover');
			$(id).attr('data-content', contents);
			$(id).attr('data-original-title', title);
		}

		function wheretoplace() {
			return 'right';
			//var width = window.innerWidth;
			//if (width < 400) {
				//return 'right';
			//}
			//return 'left';
		}

		function activate(popoverList) {
			for (var i = 0, len = popoverList.length; i < len; i++) {
				var p = popoverList[i];
				insertPopover(p.input, p.title, p.contents);
			}
			$("*[rel=popover]").popover({placement: wheretoplace});
		}

		return {
			activate: activate
		};
	}());


	function buildProjectNamespace() {
		return  {
			tooltips: tooltips,
			popovers: popovers
		};
	}

	// on document.ready
	$(function() {
		var CES = window.CES = buildProjectNamespace();
	});

}(jQuery, document, window));

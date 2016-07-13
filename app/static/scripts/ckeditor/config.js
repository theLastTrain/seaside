/**
 * @license Copyright (c) 2003-2015, CKSource - Frederico Knabben. All rights reserved.
 * For licensing, see LICENSE.md or http://ckeditor.com/license
 */

CKEDITOR.editorConfig = function( config ) {
	// Define changes to default configuration here.
	// For complete reference see:
	// http://docs.ckeditor.com/#!/api/CKEDITOR.config

	config.toolbar = [
		{ name: 'basicstyles', items: [ 'Bold', 'Italic', 'Strike', 'Underline', '-', 'Blockquote'] },
		{ name: 'paragraph', items: ['CodeSnippet', 'NumberedList', 'BulletedList' ] },
		{ name: 'links', items: [ 'Link'] },
		{ name: 'insert', items: [ 'Image', 'SpecialChar' , '-', 'RemoveFormat'] }
	];

	// Simplify the dialog windows.
	config.removeDialogTabs = 'image:advanced;link:advanced';

    config.filebrowserImageUploadUrl = '/ckupload/';
};

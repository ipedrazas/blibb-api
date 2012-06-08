

###
###
###		Blitem Unit Test
###
###
###
import sys
from os.path import join, abspath, dirname
parentpath = abspath(join(dirname(__file__), '../..'))
sys.path.append(parentpath)

from API.control.bcontrol import BControl

def getDefaultUI():
	ui =  '''
		<div id="{{c_id}}" class="bcontrols">			
			<input type="hidden" name="tid" value="{{t_id}}"/>
			<input type="hidden" name="cid" value="{{c_id}}"/>
			Title: <input type="text" name="c_title" value=""><br>
			Help text: <input type="text" name="c_help" value="" placeholder="Write here a help text to describe what this entry is for">
			<a href="#" name="ilu" class="bControlsActions" data-cid="{{c_id}}"><i class="icon-plus-sign"></i> Add to Form</a>
			<div class="bcError"></div>
		</div>
		'''
	return ui

def createBaseObject():
	c = BControl()
	c.owner = 'system'
	return c


def createSingleLineControl():
	c = createBaseObject()
	views = dict()
	c.name = 'Single Line Text Control'
	c.css = ' font-size: 100%;'
	c.ctype = 'text'
	c.typex = BControl.TEXT
	c.ui = getDefaultUI()
	views['default'] = '''
			<div id="{{ctrl_id}}_{{ctrl_order}}" class="templatedCtrl">
				<label for="{{ctrl_typex}}-{{ctrl_slug}}">{{ctrl_name}}:</label>
				<input name="{{ctrl_typex}}-{{ctrl_slug}}" placeholder="{{ctrl_help}}" size="50" type="text" />
			</div>
			'''
	c.views = views
	c.save()

# def createSingleLineControl():
# 	c = createBaseObject()
# 	views = dict()
# 	c.name = 'Single Line Text Control'
# 	c.ui = '<div id="{{c_id}}"><h3 class="click" data-tid="{{t_id}}" data-cid="{{c_id}}">Click Here to write your Field Name</h3></div>'
# 	views['default'] = '<label for="b-{{ctrl_slug}}">{{ctrl_name}}:</label><input name="b-{{ctrl_slug}}" placeholder="{{ctrl_name}}" size="50" type="text" />'
# 	c.views = views
# 	c.save()

def createDateControl():
	c = createBaseObject()
	views = dict()
	c.name = 'Date Control'
	c.css = ' font-size: 100%;'
	c.ui = getDefaultUI()
	c.ctype = 'date'
	c.typex = BControl.DATE
	views['default'] = '''
			<div id="{{ctrl_id}}_{{ctrl_order}}" class="templatedCtrl">
				<label for="{{ctrl_typex}}-{{ctrl_slug}}">{{ctrl_name}}:</label>
				<input id="datepicker" name="{{ctrl_typex}}-{{ctrl_slug}}" type="text" placeholder="{{ctrl_help}}" />
			</div>
			'''
	c.views = views
	c.save()

def createMultiLineControl():
	c = createBaseObject()
	views = dict()
	c.name = 'Multi Line Text Control'
	c.css = ' font-size: 100%;'
	c.ui = getDefaultUI()
	c.ctype = 'multitext'
	c.typex = BControl.MULTITEXT
	views['default'] = '''
			<div id="{{ctrl_id}}_{{ctrl_order}}" class="templatedCtrl">
				<label for="{{ctrl_typex}}-{{ctrl_slug}}">{{ctrl_name}}:</label>
				<textarea rows="5" cols="50" name="{{ctrl_typex}}-{{ctrl_slug}}" placeholder="{{ctrl_help}}"></textarea>
			</div>
			'''
	c.views = views
	c.save()

def createSelectControl():
	c = createBaseObject()
	views = dict()
	c.name = 'Select Text Control'
	c.css = ' font-size: 100%;'
	c.ctype = 'select'
	c.typex = BControl.LIST
	c.ui = '''
			<div id="{{ctrl_id}}_{{ctrl_order}}" class="templatedCtrl">
				<input type="hidden" name="tid" value="{{t_id}}"/>
				<input type="hidden" name="cid" value="{{c_id}}"/>
				Title: <input type="text" name="c_title" value=""><br>
				Help text: <input type="text" name="c_help" value="" placeholder="Write here a help text to describe what this entry is for">
				<div class="bcError">
				<div name="select-holder" id="{{c_id}}" >
					<form class="well form-inline">
						<input type="text" class="input-large" placeholder="Name" id="entryName">
						<a  class="btn" id="entryButton" href="#">Add Entry to List</a>
					</form>
					<label for="b-{{ctrl_slug}}">{{ctrl_name}}:</label>
					<select id="superselect" name="b-{{ctrl_slug}}"></select>
				</div>
				<a href="#" name="ilu" class="bControlsActions" data-cid="{{c_id}}"><i class="icon-plus-sign"></i> Add to Form</a>
			</div>
			'''

	views['default'] = '<label for="b-{{ctrl_slug}}">{{ctrl_name}}:</label><input name="b-{{ctrl_slug}}" placeholder="{{ctrl_help}}" size="50" type="text" />'
	c.views = views
	c.save()

def createUploadImages():
	c = createBaseObject()
	views = dict()
	c.name = 'Upload Image Control'
	c.css = ' font-size: 100%;'
	c.ui =  c.ui = getDefaultUI()
	c.ctype = 'image'
	c.typex  = BControl.IMAGE
	views['default'] =  '''<input type="hidden" name="{{ctrl_typex}}-{{ctrl_slug}}" value="" id="bi-{{ctrl_id}}_{{ctrl_order}}">
<div>
    {{ctrl_name}}:
    <div id="imageUploader" name="uploadImage"><noscript><p>Please enable JavaScript to use file uploader.</p><!-- or put a simple form for upload here --></noscript>         
    </div>
	<div id="im_{{ctrl_slug}}" style="display:none"><img id="img_{{ctrl_slug}}"  alt="thumbnail" width="260"/></div>
</div>
<script src="js/fileuploader.js" type="text/javascript"></script>
<script>
    $(function() {                
        createUploader('imageUploader', '[[id]]', '[[key]]');
    }); 
    function createUploader(element, bid, key){            
        var uploader = new qq.FileUploader({
            element: document.getElementById(element),
            action: 'actions/uploadImage',
            allowedExtensions: ['jpg', 'jpeg', 'png', 'gif'],
             params: {
                bid: bid,
                k: key
            },
            onComplete: function(id, fileName, responseJSON){
            	var resp =  responseJSON.id;
            	$('#bi-{{ctrl_id}}_{{ctrl_order}}').val(resp);
            	var srcI = "actions/getImage?id=" + resp;
            	$("#img_{{ctrl_slug}}").attr("src",srcI);
            	$("#im_{{ctrl_slug}}").show();
            },
        });
    }
</script>''' 
	c.views = views
	c.save()


def createUploadMusic():
	c = createBaseObject()
	views = dict()
	c.name = 'Upload MP3 Control'
	c.css = ' font-size: 100%;'
	c.ctype = 'song'
	c.typex = BControl.MP3
	c.ui =  c.ui = getDefaultUI()
	views['default'] =  '''<input type="hidden" name="{{ctrl_typex}}-{{ctrl_slug}}" value="" id="bi-{{ctrl_id}}-{{ctrl_slug}}">
<div>
    {{ctrl_name}}:
    <div id="musicUploader" name="uploadMusic"><noscript><p>Please enable JavaScript to use file uploader.</p><!-- or put a simple form for upload here --></noscript>         
    </div>
    
   <div id="song_{{ctrl_id}}_{{ctrl_order}}" ></div>
</div>
<script src="js/fileuploader.js" type="text/javascript"></script>
<script>
    $(function() {                
        createUploader('musicUploader', '[[id]]', '[[key]]');
    }); 
    function createUploader(element, bid, key){            
        var uploader = new qq.FileUploader({
            element: document.getElementById(element),
            action: 'actions/uploadMP3',
            allowedExtensions: ['mp3', 'oog'],
             params: {
                bid: bid,
                k: key
            },
            onComplete: function(id, fileName, responseJSON){
            	var resp =  responseJSON.id;
            	$('#bi-{{ctrl_id}}-{{ctrl_slug}}').val(resp);         
            	$("#song_{{ctrl_id}}_{{ctrl_order}}").html(responseJSON.song.song);
            	$('.qq-upload-failed-text').hide();
            },
        });
    }
</script>''' 
	c.views = views
	c.save()

def createBookmarkControl():
	c = createBaseObject()
	views = dict()
	c.name = 'Bookmark Control'
	c.css = ' font-size: 100%;'
	c.typex = BControl.URL
	c.ui = getDefaultUI()
	views['default'] = '''
			<div id="{{ctrl_id}}_{{ctrl_order}}" class="templatedCtrl">
				<label for="{{ctrl_typex}}-{{ctrl_slug}}">{{ctrl_name}}:</label>
				<input name="{{ctrl_typex}}-{{ctrl_slug}}" placeholder="{{ctrl_help}}" size="50" type="text" />
			</div>
			'''
	c.views = views
	c.save()

def createTwitterControl():
	c = createBaseObject()
	views = dict()
	c.name = 'Twitter Control'
	c.css = ' font-size: 100%;'
	c.ctype = 'text'
	c.typex = BControl.TWITTER
	c.ui = getDefaultUI()
	views['default'] = '''
			<div id="{{ctrl_id}}_{{ctrl_order}}" class="templatedCtrl">
				<label for="{{ctrl_typex}}-{{ctrl_slug}}">{{ctrl_name}}:</label>
				<input name="{{ctrl_typex}}-{{ctrl_slug}}" placeholder="{{ctrl_help}}" size="50" type="text" />
			</div>
			'''
	c.views = views
	c.save()

def createAll():
	createSingleLineControl()
	createMultiLineControl()
	createDateControl()
	# createSelectControl()
	createUploadImages()
	createUploadMusic()
	createBookmarkControl()
	createTwitterControl()
	
print 'Script to create BControls'


# createAll()
# createSingleLineControl()
# createMultiLineControl()
# createDateControl()
# # createSelectControl()
# createUploadImages()
# createUploadMusic()
# createBookmarkControl()
createTwitterControl()
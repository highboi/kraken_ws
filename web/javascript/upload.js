//upload text content
document.getElementById("textuploadbtn").addEventListener("click", async (event) => {
	//get the form
	var textform = document.getElementById("textupload");

	//get attributes of the form
	var uploadObj = {title: textform.getElementById("title").value, content: textform.getElementById("body").value, peerid: tsunami.userid, type: "text"};

	//make a unique id for this content
	var contentid = Date.now().toString() + uploadObj.title;

	//store the data on the network
	await tsunami.putData(contentid, JSON.stringify(uploadObj));
});

//upload video content
document.getElementById("videouploadbtn").addEventListener("click", async (event) => {
	//get the form
	var videoform = document.getElementById("videoupload");

	//generate a unique id for this content
	var contentid = Date.now().toString() + videoform.getElementById("title").value;

	//generate unique file id
	var fileid = Date.now().toString() + videoform.getElementById("videofile").files[0].name;

	//get form attributes
	var uploadObj = {title: videoform.getElementById("title").value, content: fileid, peerid: tsunami.userid, type: "video"};

	//torrent the file onto the network
	await tsunami.torrentFile(videoform.getElementById("videofile").files[0], fileid);

	//store the data on the network
	await tsunami.putData(contentid, JSON.stringify(uploadObj));
});

//upload image content
document.getElementById("imageuploadbtn").addEventListener("click", async (event) => {
	//get the form
	var imageform = document.getElementById("imageupload");

	//generate a unique id for this content
	var contentid = Date.now().toString() + imageform.getElementById("title").value;

	//generate unique file id
	var fileid = Date.now().toString() + imageform.getElementById("imagefile").files[0].name;

	//get form attributes
	var uploadObj = {title: imageform.getElementById("title").value, content: fileid, peerid: tsunami.userid, type: "image"};

	//torrent the file onto the network
	await tsunami.torrentFile(imageform.getElementById("imagefile").files[0], fileid);

	//store the data on the network
	await tsunami.putData(contentid, JSON.stringify(uploadObj));
});

//upload audio content
document.getElementById("audiouploadbtn").addEventListener("click", async (event) => {
	//get the form
	var audioform = document.getElementById("audioupload");

	//generate a unique id for this content
	var contentid = Date.now().toString() + audioform.getElementById("title").value;

	//generate unique file id
	var fileid = Date.now().toString() + audioform.getElementById("audiofile").files[0].name;

	//get form attributes
	var uploadObj = {title: audioform.getElementById("title").value, content: fileid, peerid: tsunami.userid, type: "audio"};

	//torrent the file onto the network
	await tsunami.torrentFile(audioform.getElementById("audiofile").files[0], fileid);

	//store the data on the network
	await tsunami.putData(contentid, JSON.stringify(uploadObj));
});


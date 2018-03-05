var ticket_data = {id : 0, description:'', comment:''};

var comments = [
    {id: "0", comment: "Katz", prob:'100%'},
    {id: "1", comment: "Lerche2", prob:'100%'},
    {id: "2", comment: "Katz", prob:'100%'},
    {id: "3", comment: "Katz", prob:'100%'},
    {id: "4", comment: "Katz", prob:'100%'}
  ]
var context = {
		comments: comments
	};

var client = ZAFClient.init();

$(function() {
  client = ZAFClient.init();
  client.invoke('resize', { width: '100%', height: '400px' });
  
  firstData();
  getResponseData(ticket_data.description, client);
});

function firstData() {
  Promise.all([client.get('ticket.id'),client.get('ticket.description')]).then(
	  function fullfilled(contents){
		  ticket_data.id = contents[0]['ticket.id'];
		  ticket_data.description = contents[1]['ticket.description'];
		  }
	  );
}

function showInfo(data) {
  var source = $("#add_task-hdbs").html();
  var template = Handlebars.compile(source);
  var html = template(context);
  $("#content").html(html);
}

function applyComment(event, id) {
	client.set('comment.text', comments[id].comment);
    client.invoke('notify', 'Comment added to Ticket.');
};

function showError() {
  var error_data = {
    'status': 404,
    'statusText': 'Not found'
  };
  var source = $("#error-template").html();
  var template = Handlebars.compile(source);
  var html = template(error_data);
  $("#content").html(html);
}

function getResponseData(task, client) {
	var resp_data = '';
	var settings = {
	    url: 'http://13.71.115.220/intent',
	    //headers: {"Authorization": "Bearer 0/68e815b2751c4bf45d1e25295f8fb39a"},
	    type: 'POST',
	    contentType: 'application/json',
	    data: JSON.stringify(task),
	    dataType: 'json'
	  }; 

  client.request(settings).then(
    function(data) {
      client.invoke('notify', 'Received Ticket Responses. ');
//    $('#task-form')[0].reset();
      ticket_data.comment = data.Intent_values;
      showInfo(ticket_data.comment);
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      client.invoke('notify', msg, 'error');
    }
  );
}
var ticket_data = {id : 0, description:'', comment:''};
var comment_data = {
		'Comment_1': '',
		'Comment_2': '',
		'Comment_3': '', 
		'Comment_4': '',
		'Comment_5': '',
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
		  console.log(ticket_data.id); 
		  console.log(ticket_data.description); 
	  }
	  );
}

function showInfo(data) {
  comment_data.Comment_1 = data;
  var source = $("#add_task-hdbs").html();
  var template = Handlebars.compile(source);
  var html = template(comment_data);
  $("#content").html(html);
  $("#add-btn").click(function(event) {
    addCommentToTicket(data, ticket_data.id)
    client.invoke('notify', 'Comment added to Ticket. ', 'error');
  });
}

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

function addCommentToTicket(data, ticket_id) {
	client.set('comment.text', comment_data.Comment_1)

  /*var data = { "ticket": { "comment": { "body": comment_data.Comment_1, "public": true } } };
	var settings = {
	    url: '/api/v2/tickets/' + ticket_data.id + '.json',
	    dataType: 'JSON',
	    type: 'PUT',
	    contentType: 'application/json',
	    data: JSON.stringify(data)
	};
    client.request(settings).then(
	    function(data) {
	      client.invoke('notify', 'Comment has been added to Ticket.');
	    },
	    function(response) {
	      var msg = 'Error ' + response.status + ' ' + response.statusText;
	      client.invoke('notify', msg, 'error');
	      console.log(response);
	    }
    );	*/
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
      console.log(ticket_data.comment);
      showInfo(ticket_data.comment);
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      client.invoke('notify', msg, 'error');
      console.log(response);
    }
  );
}
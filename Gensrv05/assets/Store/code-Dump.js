function getCommentData(ticket_id){
	var settings = {
		url: '/api/v2/tickets/'+ ticket_id + '/comments.json',
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json'
	    	}; 

	client.request(settings).then(
    function(data) {
        //console.log(data);
    	syncTicketData(data); 
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('Error : '+ msg);
    }
	);
}

var ticket_json_data = [];
function syncAllTicketData(url2){
	console.log('syncAllTicketData:');
	var settings = {
		url: url2,
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json'
	    	}; 
	client.request(settings).then(
    function(data) {
        if (data['next_page'] != null) {
        	ticket_json_data.push(data);
        	getTicketDataRecurssive(data['next_page']);
        	return;
        }
    	uploadTicketData(ticket_json_data); 
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('Error : '+ msg);
    }
	);
}


function getTicketData(){
	if (called_flag == false) {
		called_flag = true;
	} else {
		return;
	}
	var settings = {
		url: '/api/v2/tickets.json',
	    type: 'GET',
	    contentType: 'application/json',
	    dataType: 'json'
	    	};

	client.request(settings).then(
    function(data) {
        //console.log(data);
    	pastticket_data.upload_ticket_data = data.tickets
    	pastticket_data.ticket_data = ticket_data
    	syncTicketData();
    },
    function(response) {
      var msg = 'Error ' + response.status + ' ' + response.statusText;
      //client.invoke('notify', msg, 'error');
      console.log('Error : '+ msg);
    }
	);
}
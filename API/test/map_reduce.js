
m1 = function(){ 
	emit(this.n, this.d);			
}

r3 = function(doc, values){ 
	var c = 0;
	var ssum = 0; 
	values.forEach(
		function(f) { 
			ssum += f; 
			c++;
		}
	); 
	return ssum/c;
};

res = db.events.mapReduce(m1, r3, {out: 'averages_m'});


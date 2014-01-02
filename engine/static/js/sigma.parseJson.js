/**
 * Created by droghetti on 12/30/13.
 */
// Scott Hale (Oxford Internet Institute)
// Requires sigma.js and jquery to be loaded
// based on parseGexf from Mathieu Jacomy @ Sciences Po Médialab & WebAtlas
sigma.publicPrototype.parseJson = function(jsonPath,callback) {
	var sigmaInstance = this;
	var edgeId = 0;

	jQuery.getJSON(jsonPath, function(data) {
		for (i=0; i<data.nodes.length; i++){
            H=600
            W=$("#sigma-example-parent").width()
            data.nodes[i].x = W*Math.random();
            data.nodes[i].y = H*Math.random();
            data.nodes[i].color = 'rgb(49,163,84)';

			var id=data.nodes[i].id;
			sigmaInstance.addNode(id,data.nodes[i]);
		}
		for(j=0; j<data.links.length; j++){
			var edgeNode = data.links[j];
            data.links[j].size = data.links[j].values

			var source = edgeNode.source;
			var target = edgeNode.target;

			sigmaInstance.addEdge(edgeId++,source,target,edgeNode);
		}
		if (callback) callback.call(this);//Trigger the data ready function
    }).done(function(){
            sigmaInstance.draw();
    });
	//end jquery getJSON function
};//end sigma.parseJson function
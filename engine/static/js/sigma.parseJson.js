/**
 * Created by droghetti on 12/30/13.
 */
// Scott Hale (Oxford Internet Institute)
// Requires sigma.js and jquery to be loaded
// based on parseGexf from Mathieu Jacomy @ Sciences Po Médialab & WebAtlas
sigma.publicPrototype.parseJson = function(jsonPath,callback) {
	var sigmaInstance = this;
	var edgeId = 0;
    console.log('qui')
    console.log(jsonPath)
	jQuery.getJSON(jsonPath, function(data) {
        console.log(data)
		for (i=0; i<data.nodes.length; i++){
			var id=data.nodes[i].id;
			sigmaInstance.addNode(id,data.nodes[i]);
		}
		for(j=0; j<data.links.length; j++){
			var edgeNode = data.links[j];

			var source = edgeNode.source;
			var target = edgeNode.target;

            if ((data.links[j].values *100 ) > 0.5 ){
                sigmaInstance.addEdge(edgeId++,source,target,edgeNode);
            }
//			sigmaInstance.addEdge(edgeId++,source,target,edgeNode);
		}
		if (callback) callback.call(this);//Trigger the data ready function
	});//end jquery getJSON function
};//end sigma.parseJson function
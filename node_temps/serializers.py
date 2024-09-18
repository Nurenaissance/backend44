from rest_framework import serializers
from .models import NodeTemplate

class NodeTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NodeTemplate
        fields = "__all__"

    def cleanup(self, node_data):
        nodes = node_data.get('nodes', [])
        edges = node_data.get('edges', [])

        temp = True
        for node in nodes:
            if node['id'] == "start":
                if temp == False:
                    nodes.remove(node)
                else:
                    temp = False
                
        
        temp = True
        for edge in edges:
            if edge['id'] == "start-edge":
                if temp == False:
                    edges.remove(edge)
                else:
                    temp = False
        
        node_data['nodes'] = nodes
        node_data['edges'] = edges

        return node_data

    def create(self, validated_data):
        node_data = validated_data.get('node_data', {})
        validated_data['node_data'] = self.cleanup(node_data)
        return super().create(validated_data)
    
    def update(self, instance, validated_data):
        node_data = validated_data.get('node_data', instance.node_data)
        validated_data['node_data'] = self.cleanup(node_data)
        return super().update(instance, validated_data)


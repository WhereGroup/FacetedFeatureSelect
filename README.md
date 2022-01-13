# Faceted Feature Select for QGIS
A user-definable faceted feature selection form for QGIS. Experimental work-in-progress prototype.

We are playing around with different approaches to provide users with a graphical way of setting up a custom form to filter and select features by multiple, potentially hierarchical or mixed criteria.

This current prototyp allows users to specify attribute fields and filter types to search matching features. The map is filtered to the matching features and the user can choose to take matches into a selection. Compared to the built-in search and filter options, this allows using the same attribute field multiple once and provides real-time feedback on the map canvas.

There will be bugs and the usage is not too user-friendly at the moment. It is marked experimental for a reason. We have lots of ideas and plans to play with in the future and thus this plugin will probably change a lot until it is fit for end users. Examples are performance improvements, other chaining of facets than `AND`, other filtering approaches than the "SQL"-ish layer filter, loading/saving of form configurations, etc.

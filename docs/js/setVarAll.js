var setVars = {

	"all": group_all,
	"adipose": group_all_adipose,
	"bone": group_all_bone,
	"cells": group_all_cells,
	"exosome": group_all_evboost,
	"media": group_all_media,
	"umbilical_cord": group_all_umbilical_cord,
	"table_data": tableall_table,
	"filename": "2014-2022_PubsCitingRoosterBio",
	"tabname": "2014-2022"
};


console.log("setVars = ")
console.log(setVars)

var mapMakerAll = mapMaker(setVars);
var tableMakerAll = tableMaker(setVars);

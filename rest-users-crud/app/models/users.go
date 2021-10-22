package models

import "gopkg.in/mgo.v2/bson"

type User struct {
	ID          bson.ObjectId `bson:"_id" json:"id"`
	Name        string        `bson:"name" json:"name"`
	Dob         string        `bson:"dob" json:"dob"`
	Address     string        `bson:"address" json:"address"`
	Description string        `bson:"description" json:"description"`
	CreatedAt   string        `bson:"createdAt" json:"createdAt"`
}
# Paths for Flask
This file acts as documentation for the routes that the Flask server will implement.

Every path will actually route through Ory oathkeeper.

## Authentication
Auth is handled by Ory Kratos.

## Users
`PUT /user/:user_id`

- creates a new user if it doesn't already exist

`GET /user/:user_id` 

- returns list of user's projects 

if user_id == session.id (client side)
- display edit button for each project

## Project

`POST /project/new`

- creates a new project, redirect to `/project/:new_project_id`

`POST,DELETE /project/:project_id/delete`

- deletes a project, redirect to `/user/:user_id`

`POST,PATCH /project/:project_id/edit?param1=value1&param2=value2`

- edits project information

`GET /project/:project_id`

- returns list of nodes and edges belonging to project `project_id`

`GET /project/:project_id/resource/:resource_id/edit?param1=value1&param2=value2`

- edits the resource information from this project's context
- (include project to deal with permissions more easily next time when multiple projects share the same resource)

`PUT /project/:project_id/new?item=`

- item is either `node` or `relationship`, creates item in project

## Misc

`GET /explore?params=sort_by`

- returns a list of projects sorted by `sort_by`
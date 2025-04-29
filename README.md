# MegaCloud MCP Server

MCP Server for the MegaCloud API, enabling middleware management, information checking, and more.

### Features

- Host checking
- Middleware lifecycle (create, start, stop, restart, delete, add node, delete node)
- Status and configuration inspection
- Backups
- Node-level management

## Tools

Below is the list of your MCP tools converted into the requested format:

1. `list_available_hosts`  
   - List all available hosts that can be used to deploy middleware.  
   - Inputs: _None_  
   - Returns: List of host objects.

2. `list_middleware_types`  
   - List all middleware types.  
   - Inputs: _None_  
   - Returns: List of supported middleware‐type identifiers.

3. `list_middleware_instances`  
   - List all middleware instances that are currently deployed.  
   - Inputs: _None_  
   - Returns: List of middleware instance objects

4. `restart_middleware`  
   - Restart a middleware instance.  
   - Inputs:  
     - `middleware_instance_name` (string): Middleware Instance Name  
   - Returns: Operation result / status confirmation

5. `stop_middleware`  
   - Stop a middleware instance.  
   - Inputs:  
     - `middleware_instance_name` (string): Middleware Instance Name  
   - Returns: Operation result / status confirmation

6. `start_middleware`  
   - Start a middleware instance.  
   - Inputs:  
     - `middleware_instance_name` (string): Middleware Instance Name  
   - Returns: Operation result / status confirmation

7. `delete_middleware`  
   - Delete a middleware instance.  
   - Inputs:  
     - `middleware_instance_name` (string): Middleware Instance Name  
   - Returns: Operation result / deletion confirmation

8. `get_middleware_info`  
   - Get all information of a middleware instance, like configs, nodes, etc.  
   - Inputs:  
     - `middleware_instance_name` (string): Middleware Instance Name  
   - Returns: Detailed middleware-instance object

9. `get_middleware_status`  
   - Get the status of a middleware instance.  
   - Inputs:  
     - `middleware_instance_name` (string): Middleware Instance Name  
   - Returns: Status object (e.g. running/stopped + node list)

10. `backup_middleware`  
    - Backup a middleware instance.  
    - Inputs:  
      - `middleware_instance_name` (string): Middleware Instance Name  
    - Returns: Backup task details / confirmation

11. `list_middleware_instance_nodes`  
    - List all nodes of a middleware instance.  
    - Inputs:  
      - `middleware_instance_name` (string): Middleware Instance Name  
    - Returns: Array of node objects

12. `remove_middleware_instance_nodes`  
    - Remove nodes from a middleware instance.  
    - Inputs:  
      - `name` (string): Name of the middleware instance  
      - `node_names` (array[string]): Node Names to remove  
    - Returns: Operation result / updated node list

13. `create_single_redis_middleware`  
    - Create a single Redis instance.  
    - Inputs:  
      - `host_name` (string): Host Name (required)  
      - `max_memory_in_gb` (integer, default 4): Max Memory In GB  
      - `name` (string | null, default null): Instance Name (optional)  
    - Returns: Newly created middleware-instance object

14. `create_redis_cluster_middleware`  
    - Create a Redis Cluster middleware instance.  
    - Inputs:  
      - `name` (string | null, default null): Cluster Name (optional)  
      - `max_memory_in_gb` (integer, default 4): Max Memory In GB per node  
      - `master_host_names` (array[string]): Master Host Names (required)  
      - `replica_host_names` (array[string]): Replica Host Names (required)  
    - Returns: Newly created cluster-instance object

15. `add_redis_nodes`  
    - Add nodes to a Redis middleware instance.  
    - Inputs:  
      - `name` (string): Name of the Redis instance (required)  
      - `master_host_names` (array[string] | null, default null): New Master Hosts (optional)  
      - `replica_host_names` (array[string] | null, default null): New Replica Hosts (optional)  
    - Returns: Operation result / updated cluster topology


## Setup

### Obtain an Auth Token

Log in to the MegaCloud console, open your browser’s Network tab while loading any API call, and extract the `Authorization: Bearer <token>` header value.

### Install

Clone the repo:
```
git clone https://github.com/megaease/megacloud-mcp.git
```

Then run
```
pip install "mcp[cli]"
```

Remember to install `mcp` command globally for all users.

### VS Code Integration

#### Cline
Install the `Cline` for VS Code extension. 

Set MegaCloud MCP server with following config:

```json
{
  "mcpServers": {
    "megacloud-mcp": {
      "type": "stdio",
      "command": "mcp",
      "args": [
        "run",
        "<your-repo-dir>/megacloud-mcp/megacloud_mcp/__main__.py"
      ],
      "env": {
        "MEGACLOUD_AUTHTOKEN": "<your-auth-token>"
      }
    }
  }
}
```
#### GitHub Copilot
```json
{
    "mcp": {
        "servers": {
            "test-megacloud-mcp": {
                "type": "stdio",
                "command": "mcp",
                "args": [
                    "run",
                    "<your-repo-dir>/megacloud-mcp/megacloud_mcp/__main__.py"
                ],
                "env": {
                    "MEGACLOUD_AUTHTOKEN": "<your-auth-token>"
                }
            }
        }
    }
}
```
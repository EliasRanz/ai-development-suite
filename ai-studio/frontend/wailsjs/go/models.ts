export namespace entities {
	
	export class Configuration {
	    id: string;
	    name: string;
	    type: string;
	    executable_path: string;
	    working_dir: string;
	    port: number;
	    host: string;
	    arguments: string[];
	    environment: Record<string, string>;
	    auto_start: boolean;
	    // Go type: time
	    created_at: any;
	    // Go type: time
	    updated_at: any;
	
	    static createFrom(source: any = {}) {
	        return new Configuration(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.id = source["id"];
	        this.name = source["name"];
	        this.type = source["type"];
	        this.executable_path = source["executable_path"];
	        this.working_dir = source["working_dir"];
	        this.port = source["port"];
	        this.host = source["host"];
	        this.arguments = source["arguments"];
	        this.environment = source["environment"];
	        this.auto_start = source["auto_start"];
	        this.created_at = this.convertValues(source["created_at"], null);
	        this.updated_at = this.convertValues(source["updated_at"], null);
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}
	export class AIToolInstance {
	    id: string;
	    config: Configuration;
	    status: string;
	    pid: number;
	    // Go type: time
	    started_at?: any;
	    // Go type: time
	    stopped_at?: any;
	    last_error: string;
	    log_file_path: string;
	
	    static createFrom(source: any = {}) {
	        return new AIToolInstance(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.id = source["id"];
	        this.config = this.convertValues(source["config"], Configuration);
	        this.status = source["status"];
	        this.pid = source["pid"];
	        this.started_at = this.convertValues(source["started_at"], null);
	        this.stopped_at = this.convertValues(source["stopped_at"], null);
	        this.last_error = source["last_error"];
	        this.log_file_path = source["log_file_path"];
	    }
	
		convertValues(a: any, classs: any, asMap: boolean = false): any {
		    if (!a) {
		        return a;
		    }
		    if (a.slice && a.map) {
		        return (a as any[]).map(elem => this.convertValues(elem, classs));
		    } else if ("object" === typeof a) {
		        if (asMap) {
		            for (const key of Object.keys(a)) {
		                a[key] = new classs(a[key]);
		            }
		            return a;
		        }
		        return new classs(a);
		    }
		    return a;
		}
	}

}

export namespace os {
	
	export class Process {
	    Pid: number;
	
	    static createFrom(source: any = {}) {
	        return new Process(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.Pid = source["Pid"];
	    }
	}

}

export namespace services {
	
	export class SystemInfo {
	    os: string;
	    architecture: string;
	    cpu_cores: number;
	    memory: number;
	    disk_space: number;
	
	    static createFrom(source: any = {}) {
	        return new SystemInfo(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.os = source["os"];
	        this.architecture = source["architecture"];
	        this.cpu_cores = source["cpu_cores"];
	        this.memory = source["memory"];
	        this.disk_space = source["disk_space"];
	    }
	}

}

export namespace usecases {
	
	export class CreateConfigRequest {
	    name: string;
	    type: string;
	    executable_path: string;
	    working_dir: string;
	    port: number;
	    host: string;
	    arguments: string[];
	    environment: Record<string, string>;
	    auto_start: boolean;
	
	    static createFrom(source: any = {}) {
	        return new CreateConfigRequest(source);
	    }
	
	    constructor(source: any = {}) {
	        if ('string' === typeof source) source = JSON.parse(source);
	        this.name = source["name"];
	        this.type = source["type"];
	        this.executable_path = source["executable_path"];
	        this.working_dir = source["working_dir"];
	        this.port = source["port"];
	        this.host = source["host"];
	        this.arguments = source["arguments"];
	        this.environment = source["environment"];
	        this.auto_start = source["auto_start"];
	    }
	}

}


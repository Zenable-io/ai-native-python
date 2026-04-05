#!/usr/bin/env python3
"""
Validate service_definition.yaml file

This script validates the structure and content of service_definition.yaml files using Pydantic.

NOTE: This is an example validation script that should be customized for your specific use cases.
The options provided (tags, infrastructure types, etc.) are examples and should be modified to
match your organization's conventions and requirements.
"""

import sys
from pathlib import Path
from typing import Literal, Optional

import yaml
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    ValidationError,
    field_validator,
    model_validator,
)


class ServiceDefinition(BaseModel):
    model_config = ConfigDict(strict=True)
    version: Literal["0.1.0"]


class InfrastructureDependency(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    types: list[
        Literal[
            # Storage types
            "blob_storage",
            "file_storage",
            "object_storage",
            "block_storage",
            # Database types
            "sql_db",
            "nosql_db",
            "graph_db",
            "vector_db",
            "timeseries_db",
            "kvs_db",
            # Compute and processing
            "cache",
            "queue",
            "stream_processing",
            "batch_processing",
            # Networking and delivery
            "cdn",
            "load_balancer",
            "api_gateway",
            "service_mesh",
            "dns",
            "networking",
            # Security and identity
            "iam",
            "secrets",
            "vault",
            "certificate_authority",
            "local_ca",
            # ML/AI services
            "llm",
            "ml_platform",
            "model_registry",
            # Container services
            "container_registry",
            "container_orchestration",
            # Monitoring and observability
            "monitoring",
            "logging",
            "tracing",
            # Other services
            "email_service",
            "notification_service",
            "search_engine",
        ]
    ]
    local_runtime: Optional[Literal["compose", "process", "managed", "mock"]] = Field(
        None, description="How to accommodate the infrastructure locally"
    )
    version: Optional[str] = Field(
        None, pattern=r"^(0|[1-9]\d*)\.(0|[1-9]\d*)(\.(0|[1-9]\d*))?$"
    )


class ServiceDependency(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    version: Optional[str] = Field(None, pattern=r"\b[0-9a-f]{40}\b")


class DependsOnConfig(BaseModel):
    model_config = ConfigDict(strict=True)

    infrastructure: list[InfrastructureDependency] = Field(
        default_factory=list,
        description="A list of infrastructure that this component depends on",
    )
    service: list[ServiceDependency] = Field(
        default_factory=list,
        description="A list of services that this component depends on",
    )


class LanguageConfig(BaseModel):
    model_config = ConfigDict(strict=True)

    name: Literal[
        "python",
        "go",
        "javascript",
        "typescript",
        "java",
        "csharp",
        "rust",
        "ruby",
        "php",
    ]
    version: str = Field(pattern=r"^(0|[1-9]\d*)\.(0|[1-9]\d*)(\.(0|[1-9]\d*))?$")


class SoftwareConfig(BaseModel):
    model_config = ConfigDict(strict=True)

    language: LanguageConfig


class DevelopConfig(BaseModel):
    model_config = ConfigDict(strict=True)

    software: SoftwareConfig
    depends_on: Optional[DependsOnConfig] = Field(
        default_factory=DependsOnConfig,
        description="The dependencies of this service during development",
    )


class PublishConfig(BaseModel):
    model_config = ConfigDict(strict=True)

    publish_type: Literal["docker", "oci", "archive", "package", "binary", "none"]
    depends_on: Optional[DependsOnConfig] = Field(
        default_factory=DependsOnConfig,
        description="The dependencies of this service in order to build and publish",
    )


class DeployConfig(BaseModel):
    model_config = ConfigDict(strict=True)

    deploy_type: Literal[
        "sam",
        "opentofu",
        "cloudformation",
        "kubernetes",
        "helm",
        "terraform",
        "ansible",
        "none",
    ]
    depends_on: Optional[DependsOnConfig] = Field(
        default_factory=DependsOnConfig,
        description="The dependencies of this service in order to deploy",
    )
    environments: list[
        Literal[
            "development",
            "testing",
            "staging",
            "production",
            "sandbox",
            "qa",
            "uat",
            "demo",
            "dr",
        ]
    ] = Field(
        default_factory=list,
        description="A list of environments that this service can run in",
    )


class OperationsScheduleConfig(BaseModel):
    model_config = ConfigDict(strict=True)

    uptime: Literal["continuous", "on_demand", "scheduled", "business_hours"] = Field(
        "continuous", description="The uptime expectations"
    )
    days: Optional[
        list[
            Literal[
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday",
            ]
        ]
    ] = None
    start: Optional[str] = None  # RFC3339 timestamp
    end: Optional[str] = None  # RFC3339 timestamp

    @field_validator("days", "start", "end", mode="before")
    @classmethod
    def validate_scheduled_fields(cls, value, info):
        if info.data.get("uptime") == "scheduled":
            if not value:
                raise ValueError(
                    f'{info.field_name} must be specified if uptime is set to "scheduled"'
                )
        return value

    @model_validator(mode="after")
    def validate_no_extra_fields(self):
        if self.uptime != "scheduled":
            if self.days is not None or self.start is not None or self.end is not None:
                raise ValueError(
                    'days, start, and end should only be set if uptime is "scheduled"'
                )
        return self


class RuntimeEnvironmentConfig(BaseModel):
    model_config = ConfigDict(strict=True)

    authorization: dict[Literal["public"], bool]
    service_route_prefix: Optional[str] = Field(
        None,
        description="The service-specific route prefix, like data for /api/data/example and /api/data",
    )
    stage_name: Optional[str] = Field(
        None,
        description="The service-specific stage name, like current or v1; typically used for REST APIs",
    )
    uptime_sla: float = Field(95.0, description="The uptime agreement")
    uptime_slo: float = Field(99.0, description="The uptime objective")
    operations_schedule: Optional[OperationsScheduleConfig] = Field(
        default_factory=lambda: OperationsScheduleConfig(uptime="on_demand"),
        description="The operations schedule",
    )
    depends_on: Optional[DependsOnConfig] = Field(
        default_factory=DependsOnConfig,
        description="Dependencies for the specific environment",
    )


class RuntimeConfig(BaseModel):
    model_config = ConfigDict(strict=True)

    lifecycle: Literal[
        "transient",
        "experimental",
        "prototype",
        "alpha",
        "beta",
        "release_candidate",
        "ga",
        "maintenance",
        "deprecated",
        "retired",
        "pendingdeletion",
    ]
    protocols: list[
        Literal[
            "http",
            "https",
            "ws",
            "wss",
            "grpc",
            "graphql",
            "rest",
            "soap",
            "amqp",
            "mqtt",
        ]
    ] = Field(
        default_factory=list, description="The protocols that the service supports"
    )
    environments: dict[
        Literal[
            "development",
            "testing",
            "staging",
            "production",
            "sandbox",
            "qa",
            "uat",
            "demo",
            "dr",
        ],
        RuntimeEnvironmentConfig,
    ] = Field(
        ...,
        description="A dictionary of environments with their respective agreements, objectives, and dependencies",
    )
    runtime_type: Literal[
        "compose",
        "container",
        "serverless",
        "lambda",
        "function",
        "vm",
        "bare_metal",
        "kubernetes",
        "process",
        "batch",
        "cron",
        "none",
    ]
    platforms: list[Literal["linux/amd64", "linux/arm64"]] = Field(
        default_factory=list,
        description="A list of platforms that this service can run on",
    )

    @model_validator(mode="after")
    def require_protocols_sometimes(self):
        """
        Certain runtime types must specify their protocols
        """
        protocol_required_types = ["serverless", "lambda", "function", "container"]
        if self.runtime_type in protocol_required_types and not self.protocols:
            raise ValueError(
                f"{self.runtime_type} services must specify their supported protocols"
            )
        return self


class ServiceSchema(BaseModel):
    model_config = ConfigDict(strict=True)

    name: str
    description: str
    tags: list[str] = Field(
        ...,
        description="Service tags (e.g., api, backend, frontend, worker, scheduler, gateway, proxy, cache, storage)",
    )
    develop: DevelopConfig = Field(
        description="Context used when updating the service's software, tests, documentation, IaC, or other related information."
    )
    publish: Optional[PublishConfig] = Field(
        None,
        description="Details regarding how and where artifacts are published, such as container images and in-toto attestations",
    )
    deploy: Optional[DeployConfig] = Field(
        None, description="Details regarding how and where to deploy a service"
    )
    runtime: RuntimeConfig = Field(
        description="Information regarding how the post-deployment runtime and maintenance is managed for a service"
    )
    service_definition: ServiceDefinition

    @model_validator(mode="after")
    def check_lifecycle_constraints(self):
        lifecycle = self.runtime.lifecycle

        production_restricted_lifecycles = [
            "experimental",
            "prototype",
            "development",
            "deprecated",
            "sunset",
            "retired",
            "archived",
        ]

        if self.deploy and self.deploy.environments:
            if (
                lifecycle in production_restricted_lifecycles
                and "production" in self.deploy.environments
            ):
                raise ValueError(
                    f"Service {self.name}'s lifecycle of '{lifecycle}' is not allowed to deploy to production."
                )
        return self


def validate_service_definition(file_path: Path) -> bool:
    """
    Validate a service_definition.yaml file.

    Returns True if valid, False otherwise.
    """
    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        # Validate using Pydantic
        ServiceSchema(**data)
        return True

    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}")
        return False
    except ValidationError as e:
        print("Validation errors found:")
        for error in e.errors():
            location = " -> ".join(str(loc) for loc in error["loc"])
            print(f"  - {location}: {error['msg']}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False


def main():
    """Main validation function."""
    # Find service_definition.yaml
    service_def_path = Path("service_definition.yaml")
    if not service_def_path.exists():
        print("ERROR: service_definition.yaml not found")
        sys.exit(1)

    # Validate the file
    if validate_service_definition(service_def_path):
        print("✓ service_definition.yaml is valid")
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()

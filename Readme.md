        

### Flow of the gipilot the git operational ai system        
        
        
           Git Repository
                 │
        File System Events
                 │
                 ▼
          LangGraph Workflow
                 │
     ┌───────────┼────────────┐
     ▼           ▼            ▼
    Observe      Decide      Execute
     │           │            │
     └───────────┼────────────┘
                 ▼
             Verify Result
                 │
                 ▼
            Wait for Event

# Folder structure
    gitpilot/
        graph/
            builder.py
            state.py
            nodes.py
            router.py
        agents/
            planner.py
            reviewer.py
            executor.py
        tools/
            git_tools.py
            github_tools.py
            filesystem_tools.py
        llm/
            models.py
            prompts.py
        memory/
            checkpoint.py
            session.py
        services/
            watcher.py
            scheduler.py
            notifications.py
        config/
        cli/
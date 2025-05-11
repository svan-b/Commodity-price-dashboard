# Commodity Price Dashboard - Streamlit Cloud Deployment

This directory contains optimized files for deploying the Commodity Price Dashboard to Streamlit Cloud.

## Deployment Information

- **Repository**: svan-b/Commodity-price-dashboard
- **Branch**: master
- **Main file path**: streamlit_deploy/streamlit_cloud.py
- **App URL**: commodity-price-dashboard-aekclciqqiwjmvqffrfujr

## Deployment Instructions

1. Push these files to the repository
2. Log in to [Streamlit Cloud](https://streamlit.io/cloud)
3. Deploy with the following settings:
   - Repository: svan-b/Commodity-price-dashboard
   - Branch: master
   - Main file path: streamlit_deploy/streamlit_cloud.py

## Optimization Features

This deployment is optimized for Streamlit Cloud with:

- **Minimized disk usage** to prevent app crashes
- **Memory-efficient data logging** using session state
- **Streamlined dependencies** to reduce deployment size
- **Configured timeouts** and request handling
- **Session state** for data caching
- **Data caching** with TTL to improve performance
- **Reduced file operations** to prevent resource exhaustion
- **Optimized logging** to avoid filling storage

## Why This Approach Works Better

1. **Reduced Disk Usage**: The standard implementation writes logs and data snapshots to disk, which can fill up the storage on Streamlit Cloud and cause the app to crash. This version uses session state and memory caching.

2. **Resource Management**: Streamlit Cloud has resource limits, and this implementation is designed to work within those constraints by reducing CPU, memory, and disk usage.

3. **Streamlined Dependencies**: Only necessary packages are included, reducing deployment time and resource usage.

4. **Improved Caching**: Strategic caching of expensive operations (like data retrieval) improves response time and reduces load.

5. **Error Handling**: Better error handling prevents cascading failures that could bring down the app.

## Testing Locally

To test the cloud-optimized version locally before deploying:

```bash
# Run from the project root
./run_cloud.sh
```

Or manually:

```bash
python run.py --cloud
```

## Troubleshooting

If the app stops running:

1. **Check Logs**: Review the Streamlit Cloud logs for errors
2. **Resource Limits**: Ensure the app is not hitting resource limits (memory, CPU, disk)
3. **Disk Usage**: Verify the app is not writing excessively to disk
4. **Network Issues**: Check if there are network timeouts when retrieving data
5. **Browser Caching**: Try clearing browser cache if UI issues occur

## File Structure

- `streamlit_cloud.py` - Main entry point for Streamlit Cloud
- `optimized_data_logger.py` - Memory-efficient logging implementation
- `setup_cloud.py` - Ensures required directories exist
- `requirements.txt` - Optimized dependencies
- `packages.txt` - System dependencies
- `.streamlit/config.toml` - Streamlit configuration
- `.gitignore` - Excludes unnecessary files

## Maintenance

When updating the core application code, review the cloud deployment to ensure:

1. Any new dependencies are added to `requirements.txt`
2. File operations are cloud-friendly (avoid excessive writing)
3. New features respect the resource constraints of Streamlit Cloud
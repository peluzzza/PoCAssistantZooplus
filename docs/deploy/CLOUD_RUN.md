# Cloud Run — despliegue rápido (GCP)

Despliega la **misma imagen Docker** del PoC (Python 3.11 + Chroma embebido). No requiere Vertex AI RAG.

## Prerrequisitos

- `gcloud` CLI autenticado
- Proyecto GCP con facturación
- APIs: Cloud Run, Artifact Registry

## Pasos

```bash
export PROJECT_ID=your-project
export REGION=europe-west1
export SERVICE=zooplus-assistant-poc

gcloud config set project $PROJECT_ID

# Registry + build
gcloud artifacts repositories create zooplus-poc \
  --repository-format=docker --location=$REGION 2>/dev/null || true

gcloud builds submit --tag $REGION-docker.pkg.dev/$PROJECT_ID/zooplus-poc/api:v1 .

# Deploy (512Mi+ recommended for Chroma ingest at build)
gcloud run deploy $SERVICE \
  --image $REGION-docker.pkg.dev/$PROJECT_ID/zooplus-poc/api:v1 \
  --region $REGION \
  --platform managed \
  --allow-unauthenticated \
  --memory 1Gi \
  --cpu 1 \
  --timeout 120 \
  --set-env-vars ZOOPLUS_RETRIEVAL_MODE=hybrid

URL=$(gcloud run services describe $SERVICE --region $REGION --format='value(status.url)')
echo $URL

# Smoke (from your laptop)
python scripts/deploy_smoke.py $URL
```

## Limitaciones PoC en Cloud Run

- Índice Chroma va **dentro de la imagen** (rebuild para re-ingest).
- Sin volumen persistente entre revisiones salvo que montes GCS/FUSE (no incluido).
- Para Vertex embeddings / Matching Engine ver [`../DEMO.md`](../DEMO.md) sección Vertex.

## Coste orientativo

- Tráfico demo bajo: suele quedar en free tier / unos céntimos por prueba.
- Apagar: `gcloud run services delete $SERVICE --region $REGION`

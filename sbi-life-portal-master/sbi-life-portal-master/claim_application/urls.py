from django.urls import path, include

from claim_application.apis import CreateWorkOrder, GetMagicLink
from claim_application.views import DocumentAuditReportView, UploadDocuments, ListDocumentView, DeleteDocumentView, \
    AnalyticsView, DetailSummary, DetailSummaryFiles, DetailSummaryEvents, DetailEdit, RerunProcessView, \
    UpdateDocument, ApproveView, RejectView, AnalyticsExportView, DetailExcelReport, UserAuditReportView, \
    MagicLinkDetailSummary, RerunValidationView, SettingsView, HTMXFetchMasterField, HTMXFetchValidations, \
    HTMXFetchPolicyDigitalData, HTMXFetchDocumentTable, HTMXFetchDocumentEvents, FieldScoreView, \
    ChangeFieldScoreValueView, \
    ChangeFieldScoreActiveStatusView, ExportListView, HTMXFetchExportTable, BatchDeleteDocumentsView, BatchReRunValidationsView, BatchReRunDocumentsView

app_name = 'claim_application'

urlpatterns = [
    path('upload', UploadDocuments.as_view(), name='upload'),
    path('', ListDocumentView.as_view(), name='list'),
    path('<uuid:pk>/delete/', DeleteDocumentView.as_view(), name='delete'),
    path('export/', ExportListView.as_view(), name='export'),
    path('analytics/', AnalyticsView.as_view(), name='analytics'),
    path('audit-report/document/<uuid:pk>', DocumentAuditReportView.as_view(), name='audit-report'),
    path('audit-report/user/<int:pk>', UserAuditReportView.as_view(), name='audit-report'),
    path('analytics-export/', AnalyticsExportView.as_view(), name='analytics.export'),
    path('<uuid:pk>/rerun/', RerunProcessView.as_view(), name='rerun'),
    path('<uuid:pk>/rerun/validation/', RerunValidationView.as_view(), name='rerun.validation'),
    path('<uuid:pk>/', UpdateDocument.as_view(), name='update.document'),
    # path('<uuid:pk>/reviewed/approve/', ApproveView.as_view(), name='approve'),
    # path('<uuid:pk>/reviewed/reject/', RejectView.as_view(), name='reject'),
    path('magic_link/<str:key>/', MagicLinkDetailSummary.as_view(), name='magic.detail.summary'),
    path('batch/delete_documents/', BatchDeleteDocumentsView.as_view(), name='batch.delete'),
    path('batch/rerun_validation_documents/', BatchReRunValidationsView.as_view(), name='batch.rerun.validation'),
    path('batch/rerun_documents/', BatchReRunDocumentsView.as_view(), name='batch.rerun.documents'),
    path('detail/', include([
        path('<uuid:pk>/summary/', DetailSummary.as_view(), name='detail.summary'),
        path('<uuid:pk>/files/', DetailSummaryFiles.as_view(), name='detail.files'),
        path('<uuid:pk>/events/', DetailSummaryEvents.as_view(), name='detail.events'),
        path('<uuid:pk>/edit', DetailEdit.as_view(), name='detail.edit'),
        path('<uuid:pk>/excel/', DetailExcelReport.as_view(), name='detail.excel'),
    ])),
    path('settings/', include([
        path('', SettingsView.as_view(), name='settings'),
        path('field_scores/', FieldScoreView.as_view(), name='settings.field_scores'),
        path('update_field_score/', ChangeFieldScoreValueView.as_view(), name='settings.change_field_score'),
        path('update_field_status/', ChangeFieldScoreActiveStatusView.as_view(), name='settings.change_field_status'),
    ])),
    path('api/', include([
        path('create_workorder/', CreateWorkOrder.as_view(), name="api.create_work_order"),
        path('get_magic_link/', GetMagicLink.as_view(), name="api.get_magic_link")
    ])),
    path('htmx/', include([
        path('master_field/<str:page_label>', HTMXFetchMasterField.as_view(), name="htmx.fetch_master_field"),
        path('validations/<uuid:pk>/', HTMXFetchValidations.as_view(), name='htmx.fetch_validations'),
        path('policy_data/<uuid:pk>/', HTMXFetchPolicyDigitalData.as_view(), name='htmx.fetch_policy_data'),
        path('document_table/', HTMXFetchDocumentTable.as_view(),
             name='htmx.fetch_document_table'),
        path('export_table/', HTMXFetchExportTable.as_view(),
             name='htmx.fetch_export_table'),
        path('detail_events/<uuid:pk>/', HTMXFetchDocumentEvents.as_view(),
             name='htmx.fetch_detail_events'),
    ]))

]

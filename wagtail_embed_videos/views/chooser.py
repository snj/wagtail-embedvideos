import json

from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import permission_required

from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.admin.forms import SearchForm
from wagtail.search.backends import get_search_backends
from wagtail.admin.utils import PermissionPolicyChecker, popular_tags_for_model
from wagtail.core.models import Collection

from embed_video.backends import detect_backend
from wagtail.admin.forms import SearchForm
from wagtail.admin.modal_workflow import render_modal_workflow
from wagtail.admin.utils import popular_tags_for_model
from wagtail.utils.pagination import paginate

from wagtail_embed_videos.models import get_embed_video_model

from wagtail_embed_videos.permissions import permission_policy

permission_checker = PermissionPolicyChecker(permission_policy)


def get_embed_video_json(embed_video):
	"""
	helper function: given an embed video, return the json to pass back to the
	embed video chooser panel
	"""
	if embed_video.thumbnail:
		preview_embed_video = embed_video.thumbnail.get_rendition('max-130x100').url
	else:
		preview_embed_video = detect_backend(embed_video.url).get_thumbnail_url()

	return json.dumps({
		'id': embed_video.id,
		'edit_link': reverse('wagtail_embed_videos_edit_embed_video', args=(embed_video.id,)),
		'title': embed_video.title,
		'preview': {
			'url': preview_embed_video,
		}
	})


def chooser(request):
	EmbedVideo = get_embed_video_model()

	# Get embed_videos files (filtered by user permission)
	embed_videos = permission_policy.instances_user_has_any_permission_for(
		request.user, ['change', 'delete']
	)


	if request.user.has_perm('wagtail_embed_videos.add_embedvideo'):
		can_add = True
	else:
		can_add = False

	# page number
	p = request.GET.get("p", 1)

	q = None

	if 'q' in request.GET or 'p' in request.GET or 'collection_id' in request.GET:

		collection_id = request.GET.get('collection_id')
		if collection_id:
			embed_videos = embed_videos.filter(collection=collection_id)

		searchform = SearchForm(request.GET)

		q = None
		is_searching = False

		if searchform.is_valid():
			q = searchform.cleaned_data['q']
			is_searching = True

			embed_videos = embed_videos.search(q, results_per_page=10, page=p).order_by('-created_at')
		else:
			embed_videos = embed_videos.order_by('-created_at')

		# Pagination
		paginator, embed_videos = paginate(request, embed_videos, per_page=12)

		return render(request, "wagtail_embed_videos/chooser/results.html", {
			'embed_videos': embed_videos,
			'is_searching': is_searching,
			'can_add': can_add,
			'query_string': q,
		})


	searchform = SearchForm()

	collections = Collection.objects.all()
	if len(collections) < 2:
		collections = None

	embed_videos = embed_videos.order_by('-created_at')

	# Pagination
	paginator, embed_videos = paginate(request, embed_videos, per_page=12)

	return render_modal_workflow(
		request,
		'wagtail_embed_videos/chooser/chooser.html',
		'wagtail_embed_videos/chooser/chooser.js',
		{
			'embed_videos': embed_videos,
			'searchform': searchform,
			'collections': collections,
			'is_searching': False,
			'can_add': can_add,
			'query_string': q,
			'popular_tags': popular_tags_for_model(EmbedVideo),
		}
	)


def embed_video_chosen(request, embed_video_id):
	embed_video = get_object_or_404(get_embed_video_model(), id=embed_video_id)

	return render_modal_workflow(
		request, None, 'wagtail_embed_videos/chooser/embed_video_chosen.js',
		{'embed_video_json': get_embed_video_json(embed_video)}
	)
